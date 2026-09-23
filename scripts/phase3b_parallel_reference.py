#!/usr/bin/env python3
"""Resume Ensembl 88 files through verified HTTP byte ranges when FTP is slow."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys

from phase3b_acquire import RESOURCES, ROOT


def download(name, workers=8):
    kind, url, _, _, relpath, _ = RESOURCES[name]
    if kind != 'reference':
        raise ValueError('Only authoritative reference downloads use byte ranges')
    dest = ROOT / relpath
    if dest.exists():
        return dest
    headers = subprocess.check_output(['curl','-sSIL','--fail','--max-time','40',url],text=True)
    head = headers.split('\r\n\r\n')[-1]
    length = None
    for line in head.splitlines():
        if line.lower().startswith('content-length:'):
            length = int(line.split(':',1)[1].strip())
    if not length:
        raise ValueError('Authoritative server did not supply content length')
    segment_dir = dest.with_name(dest.name + '.segments')
    segment_dir.mkdir(parents=True, exist_ok=True)
    stride = (length + workers - 1)//workers
    segments = [(i, i*stride, min(length,(i+1)*stride)-1) for i in range(workers) if i*stride < length]

    def one(spec):
        i, start, end = spec
        path = segment_dir / f'{i:02d}.part'
        expected = end-start+1
        if path.exists() and path.stat().st_size == expected:
            return path
        tmp = path.with_name(path.name+'.download')
        subprocess.run(['curl','-sSL','--fail','--retry','4','--connect-timeout','30',
                        '--max-time','900','--range',f'{start}-{end}','-o',str(tmp),url],check=True)
        if tmp.stat().st_size != expected:
            raise ValueError(f'Incorrect byte-range size for {name} segment {i}')
        tmp.rename(path)
        return path

    with ThreadPoolExecutor(max_workers=workers) as pool:
        paths = list(pool.map(one,segments))
    tmp_dest = dest.with_name(dest.name+'.assembled')
    with tmp_dest.open('wb') as output:
        for path in paths:
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b''):
                    output.write(block)
    if tmp_dest.stat().st_size != length:
        raise ValueError('Incorrect assembled reference size')
    subprocess.run(['gzip','-t',str(tmp_dest)],check=True)
    tmp_dest.rename(dest)
    for path in paths:
        path.unlink()
    segment_dir.rmdir()
    print(name,length,'downloaded_and_gzip_validated',flush=True)
    return dest


if __name__ == '__main__':
    for name in sys.argv[1:]:
        download(name)
