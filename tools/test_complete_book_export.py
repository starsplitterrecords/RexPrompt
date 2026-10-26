#!/usr/bin/env python3
"""Offline export contract: complete/incomplete, structural variants and fidelity."""
from pathlib import Path
import hashlib, io, json, subprocess, sys, tempfile, zipfile
from PIL import Image
from pypdf import PdfReader

LIVE=Path(__file__).resolve().parents[1]
BUILDER=LIVE/'tools/build_complete_book.py'

def make_png(index):
    im=Image.new('RGB',(300+index*11,460+index*7),(index*23%255, index*67%255, 170))
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue(),im.size

def case(root,name,units,missing=()):
    store=root/'production/drafts'
    store.mkdir(parents=True,exist_ok=True)
    src={}
    entry={}
    series='fixture-'+name
    issue=series+'-e01'
    for i,u in enumerate(units):
        if u in missing:continue
        raw,size=make_png(i+1)
        filename='production/drafts/'+u+'.png'
        (root/filename).write_bytes(raw)
        src[u]=(raw,size)
        entry['::'.join((series,issue,u))]=dict(seriesId=series,issueId=issue,recipeId=u,
            image=filename,mimeType='image/png',status='approved-production-draft',
            sha256=hashlib.sha256(raw).hexdigest())
    inv={'schemaVersion':1,'issues':{series+'::'+issue:{'seriesId':series,'issueId':issue,
                                                    'orderPolicy':'fixture-explicit','units':units}}}
    (root/'production/book-manifests.json').write_text(json.dumps(inv))
    (store/'manifest.json').write_text(json.dumps({'drafts':entry}))
    out=root/'output'
    result=subprocess.run([sys.executable,str(root/'tools/build_complete_book.py'),
        '--series',series,'--issue',issue,'--out',str(out)],capture_output=True,text=True)
    if missing:
        assert result.returncode != 0,result.stdout
        for u in missing:assert u in result.stderr,(u,result.stderr)
        assert not list(out.glob('*.pdf')) and not list(out.glob('*.zip'))
        return
    assert result.returncode==0,result.stderr
    pdf=next(out.glob('*.pdf'));archive=next(out.glob('*.zip'))
    assert len(PdfReader(str(pdf)).pages)==len(units)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        report=json.loads(z.read('book-export-manifest.json'))
        assert report['pageCount']==len(units)
        assert report['masteringStatus'].startswith('NOT APPROVED')
        assert [x['recipeId'] for x in report['pages']]==units
        for i,page in enumerate(report['pages']):
            raw,dimensions=src[page['recipeId']]
            assert z.read(page['outputFile'])==raw
            assert page['sha256']==hashlib.sha256(raw).hexdigest()
            assert (page['nativeWidth'],page['nativeHeight'])==dimensions
            obj=PdfReader(str(pdf)).pages[i]['/Resources']['/XObject']
            image=next(iter(obj.values())).get_object()
            assert (int(image['/Width']),int(image['/Height']))==dimensions
    print('PASS',name,'complete',len(units),'pages, source hashes and PDF intrinsic XObject geometry')

with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    (root/'tools').mkdir()
    (root/'tools/build_complete_book.py').write_bytes(BUILDER.read_bytes())
    case(root,'traditional',['TS_COVER','TS_EDITOR_OPEN','TS_CAST','TS_P01','TS_P02','TS_TEASER'])
    case(root,'cover-is-page01',['VI_P01','VI_P02','VI_P03'])
    case(root,'chapter',['LT_C01_COVER','LT_C01_EDITOR_OPEN','LT_C01_P01','LT_C01_P02','LT_C01_EDITOR_NEXT'])
    case(root,'incomplete',['INC_COVER','INC_P01','INC_P02','INC_END'],missing=('INC_P02',))
print('PASS export complete/incomplete/review-only regression suite')
