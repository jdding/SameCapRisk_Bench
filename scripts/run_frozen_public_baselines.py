#!/usr/bin/env python3
"""Text-only adapter for frozen-input RRF, BGE and official SkillSight.

No labels are read here. Evaluation is a separate, post-ranking operation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import signal
import sys
import time

import numpy as np

GATE_SHA = '7da1685b088be9fb98c0e25a80f1eb5bd913cfab841ec883725a9f40b0daf0e4'
FIELDS = ['method_id', 'query_case_id', 'candidate_pool_id', 'rank', 'candidate_id', 'score']
SKILLRET_QUERY_PROMPT = 'Instruct: Given a skill search query, retrieve relevant skills that match the query\nQuery: '
METHOD_IDS = {
    'rrf': 'rrf',
    'bge': 'bge',
    'skillsight': 'skillsight_qwen3_embedding_0_6b',
    'skillret': 'skillret_embedding_0_6b',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')
    os.replace(tmp, path)


def atomic_npy(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with tmp.open('wb') as f:
        np.save(f, values)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def array_sha(values):
    values = np.ascontiguousarray(values)
    h = hashlib.sha256()
    h.update(str(values.dtype).encode())
    h.update(json.dumps(values.shape).encode())
    h.update(values.tobytes())
    return h.hexdigest()


def atomic_cache(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    values = np.asarray(values, dtype=np.float32)
    with tmp.open('wb') as f:
        np.savez(f, values=values, array_sha256=np.array(array_sha(values)))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_cache(path):
    try:
        with np.load(path, allow_pickle=False) as payload:
            values = np.asarray(payload['values'], dtype=np.float32)
            expected = str(payload['array_sha256'].item())
    except Exception as exc:
        raise ValueError('Embedding checkpoint corrupted') from exc
    if array_sha(values) != expected:
        raise ValueError('Embedding checkpoint corrupted')
    return values


def runtime_identity(method, device):
    names = ['numpy', 'scikit-learn']
    if method != 'rrf':
        names += ['torch', 'transformers', 'sentence-transformers', 'tokenizers',
                  'huggingface-hub', 'safetensors', 'protobuf', 'sentencepiece']
    result = {'python': sys.version, 'packages': {}}
    for name in names:
        try:
            result['packages'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result['packages'][name] = 'missing'
    if method != 'rrf':
        import torch
        result.update(device=device, cuda=torch.version.cuda, cudnn=torch.backends.cudnn.version(),
                      device_name=torch.cuda.get_device_name(torch.device(device)))
    return result


def tree_identity(root):
    """Bind every regular file under a model or effective runtime overlay."""
    root = Path(root)
    if not root.is_dir():
        raise ValueError('Identity root is not a directory: ' + str(root))
    volatile_suffixes = {'.pyc', '.lock', '.tmp', '.incomplete'}
    return {str(path.relative_to(root)): sha(path)
            for path in sorted(root.rglob('*'))
            if path.is_file() and '__pycache__' not in path.parts
            and path.suffix not in volatile_suffixes}


def configure_determinism(method):
    if method == 'rrf':
        return {'seed': 0, 'deterministic_algorithms': True, 'backend': 'cpu_sklearn'}
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    random.seed(0)
    np.random.seed(0)
    import torch
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    if hasattr(torch.backends.cuda, 'enable_flash_sdp'):
        torch.backends.cuda.enable_flash_sdp(False)
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        torch.backends.cuda.enable_math_sdp(True)
    return {'seed': 0, 'deterministic_algorithms': True, 'cublas_workspace_config': os.environ['CUBLAS_WORKSPACE_CONFIG'],
            'flash_sdp': False, 'memory_efficient_sdp': False, 'math_sdp': True, 'tf32': False}


def load_inputs(root, expected_gate_sha=GATE_SHA):
    root = Path(root)
    if sha(root / 'FREEZE_GATE.json') != expected_gate_sha:
        raise ValueError('Frozen gate identity mismatch')
    gate = json.loads((root / 'FREEZE_GATE.json').read_text())
    if not gate.get('experiment_ready') or gate['status'] != 'FROZEN_EXPERIMENT_READY':
        raise ValueError('Inputs not frozen')
    manifest = json.loads((root / 'BUILD_MANIFEST.json').read_text())
    if sha(root / 'BUILD_MANIFEST.json') != gate['files_sha256']['BUILD_MANIFEST.json']:
        raise ValueError('Build manifest mismatch')
    for name, expected in manifest['outputs_sha256'].items():
        if sha(root / name) != expected:
            raise ValueError('Frozen file mismatch: ' + name)
    summary = json.loads((root / 'SUMMARY.json').read_text())
    pools = {}
    seen_q = set()
    for pool, count in summary['candidate_counts'].items():
        def read(kind, id_key):
            rows = [json.loads(line) for line in (root / 'inference' / pool / (kind + '.jsonl')).read_text().splitlines()]
            if not rows or len({r[id_key] for r in rows}) != len(rows):
                raise ValueError('Empty or duplicate IDs: ' + pool + '/' + kind)
            if any(set(r) != {id_key, 'text'} or not isinstance(r['text'], str) or not r['text'].strip() for r in rows):
                raise ValueError('Inference fields/text mismatch')
            return rows
        queries, candidates = read('queries', 'query_case_id'), read('candidates', 'candidate_id')
        qids = {q['query_case_id'] for q in queries}
        if seen_q & qids or len(candidates) != count:
            raise ValueError('Pool coverage mismatch')
        seen_q |= qids
        pools[pool] = (queries, candidates)
    if len(seen_q) != gate['counts']['queries']:
        raise ValueError('Query coverage mismatch')
    return pools


class CachedEncoder:
    """Atomic batch caches, bound to the immutable run context and input text."""
    def __init__(self, model, root, mode, stop_after=0):
        self.model, self.root, self.mode = model, Path(root), mode
        self.stop_after, self.new_batches, self.reused_batches = stop_after, 0, 0

    def encode(self, texts, batch_size, show_progress=False, prompt_name=None):
        key = hashlib.sha256(json.dumps([texts, batch_size, prompt_name], ensure_ascii=False).encode()).hexdigest()
        dest = self.root / key
        if self.mode == 'skillsight':
            path = dest / 'whole_call.npz'
            if path.exists():
                values = load_cache(path)
                self.reused_batches += 1
            else:
                values = np.asarray(self.model.encode(texts, batch_size=batch_size, show_progress=show_progress,
                                                      prompt_name=prompt_name), dtype=np.float32)
                atomic_cache(path, values)
                self.new_batches += 1
                atomic_json(self.root.parent / 'checkpoint.json', {'last_batch': str(path), 'sha256': sha(path),
                            'array_sha256': array_sha(values), 'granularity': 'official_whole_encode_call'})
                if self.stop_after and self.new_batches >= self.stop_after:
                    os.kill(os.getpid(), signal.SIGTERM)
            if values.ndim != 2 or values.shape[0] != len(texts) or not np.isfinite(values).all():
                raise ValueError('Invalid embedding checkpoint shape/values')
            return values
        values = []
        for start in range(0, len(texts), batch_size):
            path = dest / ('%08d.npz' % start)
            batch = texts[start:start + batch_size]
            if path.exists():
                arr = load_cache(path)
                self.reused_batches += 1
            else:
                if self.mode == 'skillsight':
                    arr = self.model.encode(batch, batch_size=batch_size, show_progress=False, prompt_name=prompt_name)
                else:
                    arr = self.model.encode(batch, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
                arr = np.asarray(arr, dtype=np.float32)
                atomic_cache(path, arr)
                self.new_batches += 1
                atomic_json(self.root.parent / 'checkpoint.json', {'last_batch': str(path), 'sha256': sha(path),
                            'array_sha256': array_sha(arr)})
                if self.stop_after and self.new_batches >= self.stop_after:
                    os.kill(os.getpid(), signal.SIGTERM)
            if arr.ndim != 2 or arr.shape[0] != len(batch) or not np.isfinite(arr).all():
                raise ValueError('Invalid embedding checkpoint shape/values')
            values.append(arr)
        return np.concatenate(values)

    def encode_skillret(self, texts, batch_size, role):
        key = hashlib.sha256(json.dumps([texts, batch_size, role], ensure_ascii=False).encode()).hexdigest()
        path = self.root / key / 'whole_call.npz'
        if path.exists():
            values = load_cache(path)
            self.reused_batches += 1
        else:
            if role == 'query':
                values = self.model.encode_query(
                    texts, batch_size=batch_size, prompt=SKILLRET_QUERY_PROMPT,
                    show_progress_bar=True, normalize_embeddings=True)
            elif role == 'document':
                values = self.model.encode_document(
                    texts, batch_size=batch_size, show_progress_bar=True,
                    normalize_embeddings=True)
            else:
                raise ValueError('Unknown SkillRet encoding role')
            values = np.asarray(values, dtype=np.float32)
            atomic_cache(path, values)
            self.new_batches += 1
            atomic_json(self.root.parent / 'checkpoint.json', {
                'last_batch': str(path), 'sha256': sha(path),
                'array_sha256': array_sha(values),
                'granularity': 'skillret_whole_encode_call', 'role': role})
            if self.stop_after and self.new_batches >= self.stop_after:
                os.kill(os.getpid(), signal.SIGTERM)
        if values.ndim != 2 or values.shape[0] != len(texts) or not np.isfinite(values).all():
            raise ValueError('Invalid SkillRet embedding checkpoint shape/values')
        return values


def rank_rows(method, pool, queries, candidates, matrix):
    from run_generic_neural_dense_baseline import rank_from_scores
    if matrix.shape != (len(queries), len(candidates)) or not np.isfinite(matrix).all():
        raise ValueError('Invalid score matrix')
    ids = [r['candidate_id'] for r in candidates]
    index = {cid: i for i, cid in enumerate(ids)}
    rows = []
    for q, scores in zip(queries, matrix):
        for rank, cid in enumerate(rank_from_scores(q['query_case_id'], ids, scores)[:20], 1):
            rows.append(dict(method_id=method, query_case_id=q['query_case_id'], candidate_pool_id=pool,
                             rank=rank, candidate_id=cid, score=float(scores[index[cid]])))
    return rows


def validate_ranks(rows, pools):
    expected = {q['query_case_id']: (pool, {c['candidate_id'] for c in cs}, min(20, len(cs)))
                for pool, (qs, cs) in pools.items() for q in qs}
    grouped = {}
    for row in rows:
        qid = row['query_case_id']
        if qid not in expected:
            raise ValueError('Unknown query in ranks')
        pool, ids, k = expected[qid]
        if row['candidate_pool_id'] != pool or row['candidate_id'] not in ids or not np.isfinite(float(row['score'])):
            raise ValueError('Invalid ranked candidate')
        grouped.setdefault(qid, []).append(row)
    if set(grouped) != set(expected):
        raise ValueError('Missing rank queries')
    for qid, group in grouped.items():
        if sorted(int(r['rank']) for r in group) != list(range(1, expected[qid][2] + 1)) or len({r['candidate_id'] for r in group}) != len(group):
            raise ValueError('Duplicate/missing rank')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--method', choices=['rrf', 'bge', 'skillsight', 'skillret'], required=True)
    p.add_argument('--model', type=Path)
    p.add_argument('--skillsight-repo', type=Path)
    p.add_argument('--runtime-overlay', type=Path)
    p.add_argument('--device', default='cuda:0')
    p.add_argument('--doc-batch', type=int, default=4)
    p.add_argument('--query-batch', type=int, default=32)
    p.add_argument('--max-length', type=int)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--smoke-queries', type=int, default=2)
    p.add_argument('--smoke-candidates', type=int, default=32)
    p.add_argument('--stop-after-batches', type=int, default=0)
    a = p.parse_args()
    if a.max_length is None:
        a.max_length = 512 if a.method == 'bge' else 32768 if a.method == 'skillret' else 4096
    if a.stop_after_batches and not a.smoke:
        p.error('Forced interruption is smoke-only')
    determinism = configure_determinism(a.method)
    start = time.monotonic()
    pools = load_inputs(a.inputs)
    if a.smoke:
        pools = {pool: (qs[:a.smoke_queries], cs[:a.smoke_candidates])
                 for pool, (qs, cs) in pools.items()}
    model_identity = {}
    if a.method != 'rrf':
        if a.model is None or not a.model.is_dir():
            p.error('Existing model directory required')
        model_identity = tree_identity(a.model)
    runtime_overlay_identity = {}
    if a.runtime_overlay is not None:
        runtime_overlay_identity = tree_identity(a.runtime_overlay)
    import run_skillsight_baseline as ss
    sources = {n: sha(Path(__file__).parent / n) for n in [Path(__file__).name,
        'run_skillsight_baseline.py', 'run_generic_neural_dense_baseline.py', 'run_skillresolve_bench_v2_runner.py']}
    ctx = {'method': a.method, 'gate_sha256': GATE_SHA, 'model': model_identity,
           'model_path': str(a.model), 'sources': sources, 'smoke': a.smoke,
           'doc_batch': a.doc_batch, 'query_batch': a.query_batch, 'max_length': a.max_length,
           'query_prefix': ('Represent this sentence for searching relevant passages: ' if a.method == 'bge'
                            else SKILLRET_QUERY_PROMPT if a.method == 'skillret' else 'official query prompt'),
           'length_policy': 'Original model token limit retained; full input text passed to tokenizer, token-level truncation explicitly recorded; not full-token inference',
           'runtime': runtime_identity(a.method, a.device),
           'runtime_overlay_path': str(a.runtime_overlay),
           'runtime_overlay': runtime_overlay_identity,
           'determinism': determinism,
           'cache_strategy': 'atomic npz batches for BGE; atomic whole-call cache for official SkillSight sorting semantics; legacy unchecked outer cache disabled'}
    if a.method == 'skillsight':
        if a.skillsight_repo is None:
            p.error('SkillSight source required')
        ctx['official_source'] = ss.verify_skillsight_source(a.skillsight_repo)
    a.out.mkdir(parents=True, exist_ok=True)
    context_path = a.out / 'context.json'
    if context_path.exists() and json.loads(context_path.read_text()) != ctx:
        raise ValueError('Output belongs to different inputs/model/code/configuration')
    atomic_json(context_path, ctx)
    encoder = None
    if a.method == 'skillsight':
        sys.path.insert(0, str(a.skillsight_repo.parent.resolve()))
        from SkillSight.encoder import DenseEncoder
        from SkillSight.retriever import SkillSightRetriever
        ss.encode_or_load = lambda wrapped, texts, path, batch, prompt: wrapped.encode(
            texts, batch_size=batch, show_progress=False, prompt_name=prompt)
        encoder = CachedEncoder(DenseEncoder(str(a.model), device=a.device, max_seq_length=a.max_length),
                                a.out / 'batch_cache', a.method, a.stop_after_batches)
    elif a.method == 'bge':
        from run_generic_neural_dense_baseline import TransformerCLSModel
        encoder = CachedEncoder(TransformerCLSModel(str(a.model), '', a.device, a.max_length),
                                a.out / 'batch_cache', a.method, a.stop_after_batches)
    elif a.method == 'skillret':
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(
            str(a.model), trust_remote_code=True, model_kwargs={'torch_dtype': 'auto'},
            device=a.device)
        model.max_seq_length = a.max_length
        encoder = CachedEncoder(model, a.out / 'batch_cache', a.method, a.stop_after_batches)
    setup = time.monotonic() - start
    all_rows, times = [], {}
    for pool, (qs, cs) in pools.items():
        t = time.monotonic()
        if a.method == 'skillsight':
            args = argparse.Namespace(out_dir=a.out / pool, doc_batch=a.doc_batch, query_batch=a.query_batch,
                                      candidate_k=300, score_batch=64, lexical_beta=1.0, top_k=20)
            queries = [dict(query_case_id=q['query_case_id'], query_text=q['text'], stratum=pool) for q in qs]
            rows = ss.rank_pool(pool, queries, cs, encoder, SkillSightRetriever, args)
        else:
            if a.method == 'rrf':
                import run_skillresolve_bench_v2_runner as old
                ids = [c['candidate_id'] for c in cs]
                data = {'pairs': [dict(query_id=q['query_case_id'], query_text=q['text']) for q in qs],
                        'candidate_ids': ids, 'candidate_texts': [old.clean_text(c['text']) for c in cs],
                        'candidates_by_id': {c['candidate_id']: dict(c, source='unlabelled') for c in cs}}
                raw = old.compute_tfidf_scores(data)['hybrid_rrf']
                matrix = np.stack([raw[q['query_case_id']] for q in qs])
            elif a.method == 'bge':
                from run_generic_neural_dense_baseline import clean_text
                docs = encoder.encode([clean_text(c['text']) for c in cs], a.doc_batch)
                queries = encoder.encode([ctx['query_prefix'] + clean_text(q['text']) for q in qs], a.query_batch)
                matrix = queries @ docs.T
            else:
                from run_generic_neural_dense_baseline import clean_text
                docs = encoder.encode_skillret([clean_text(c['text']) for c in cs], a.doc_batch, 'document')
                queries = encoder.encode_skillret([clean_text(q['text']) for q in qs], a.query_batch, 'query')
                matrix = queries @ docs.T
            atomic_npy(a.out / (pool + '_scores.npy'), matrix)
            rows = rank_rows(METHOD_IDS[a.method], pool, qs, cs, matrix)
        all_rows.extend(rows)
        times[pool] = time.monotonic() - t
    validate_ranks(all_rows, pools)
    target = a.out / 'top20.tsv'
    temp = target.with_suffix('.tmp')
    with temp.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter='\t', extrasaction='ignore')
        w.writeheader(); w.writerows(all_rows)
    os.replace(temp, target)
    atomic_json(a.out / 'RESULT.json', {'status': 'SMOKE_COMPLETE' if a.smoke else 'RANKS_COMPLETE',
        'method': a.method, 'query_count': sum(len(qs) for qs, _ in pools.values()), 'rank_rows': len(all_rows),
        'top20_sha256': sha(target), 'context_sha256': sha(context_path), 'setup_seconds': setup,
        'inference_and_ranking_seconds': times, 'total_seconds': time.monotonic() - start,
        'training_seconds': 0, 'metric_evaluation': 'separate; no labels read here',
        'new_embedding_batches': encoder.new_batches if encoder else 0,
        'reused_embedding_batches': encoder.reused_batches if encoder else 0})
    print((a.out / 'RESULT.json').read_text(), flush=True)


if __name__ == '__main__':
    main()
