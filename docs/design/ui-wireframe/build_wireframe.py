from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html

OUT = Path(__file__).parent
W, H = 2280, 2420
im = Image.new('RGB', (W,H), '#ffffff')
d = ImageDraw.Draw(im)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>']
fontpath = next((str(p) for p in [Path('C:/Windows/Fonts/arial.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf')] if p.exists()), None)
boldpath = next((str(p) for p in [Path('C:/Windows/Fonts/arialbd.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'), Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf')] if p.exists()), fontpath)
if fontpath is None:
    raise RuntimeError('Install Arial, DejaVu Sans or Liberation Sans to regenerate the wireframe.')
def text(x,y,s,size=18,bold=False,color='#222222'):
    f=ImageFont.truetype(boldpath if bold else fontpath,size)
    d.text((x,y),s,font=f,fill=color)
    svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}">{html.escape(s)}</text>')
def box(x,y,w,h,fill='#ffffff',stroke='#777777'):
    d.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke,width=1)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
def field(x,y,w,label,value):
    text(x,y,label,16,True);box(x,y+25,w,36);text(x+10,y+32,value,16)
def button(x,y,w,label,primary=False):
    box(x,y,w,38,'#dddddd' if primary else '#ffffff','#333333');text(x+12,y+9,label,16,primary)
def note(x,y,w,msg):
    box(x,y,w,38,'#eeeeee');text(x+12,y+10,msg,16)
def table(x,y,width,headers,rows,colwidths):
    box(x,y,width,34,'#dddddd'); pos=x
    for h,cw in zip(headers,colwidths): text(pos+9,y+9,h,15,True);pos+=cw
    for i,row in enumerate(rows):
        yy=y+34+i*39;box(x,yy,width,39,'#ffffff' if i%2==0 else '#f5f5f5');pos=x
        for val,cw in zip(row,colwidths):text(pos+9,yy+11,val,15);pos+=cw
def panel(x,y,n,title,active):
    text(x,y,f'{n:02d}  {title}',27,True)
    y+=47;box(x,y,1080,640)
    box(x,y,1080,52,'#dddddd');text(x+20,y+17,'EDWARDS  |  Materials Database',19,True);text(x+837,y+18,'User  |  Sign out',16)
    for i,label in enumerate(['Upload','Review queue','Materials','Analysis']):
        bx=x+20+i*170
        box(bx,y+65,160,35,'#800020' if label==active else '#fff7f8','#800020')
        text(bx+12,y+74,label,16,label==active,'#ffffff' if label==active else '#800020')
    return x+24,y+119

text(40,24,'ONLINE MATERIALS DATABASE  /  UI WIREFRAMES',36,True)
text(40,74,'Task #41  |  Low-fidelity desktop layouts  |  Illustrative data only  |  Access depends on assigned permissions',20)

x,y=panel(40,130,1,'Document upload','Upload')
text(x,y,'Upload CoCs and material test reports',24,True)
box(x,y+44,1032,108,'#f5f5f5');text(x+270,y+65,'Drop PDF files here or choose files',23);text(x+324,y+107,'Digital and scanned PDFs supported',17)
field(x,y+171,480,'Default document type (editable per file)','CoC / Internal test report [select]')
field(x+512,y+171,520,'Vendor (if known)','Select vendor or leave unspecified')
table(x,y+253,1032,['Selected file','Type [select]','Upload status'],[['vendor-coc-001.pdf','CoC','Uploaded'],['internal-report-002.pdf','Test report','Uploaded']], [550,200,282])
button(x,y+386,215,'Upload and process',True);button(x+235,y+386,150,'Clear files')
note(x,y+442,1032,'Feedback: upload accepted -> processing -> ready for review. Invalid file: PDF required.')

x,y=panel(1160,130,2,'Processing and review queue','Review queue')
text(x,y,'Document processing and review queue',24,True)
field(x,y+47,480,'Find document','Filename, material ID or vendor')
field(x+512,y+47,520,'Status','All / Processing / Failed / Unsupported / Pending / Flagged')
table(x,y+135,1032,['Document','Status','Feedback','Action'],[['vendor-coc-001.pdf','Flagged','2 fields need review','Open review'],['internal-report-002.pdf','Pending','Awaiting approval','Open review'],['vendor-coc-003.pdf','Processing','Extracting fields','View status'],['vendor-coc-004.pdf','Failed','PDF could not be read','Retry / replace']], [320,160,345,207])
note(x,y+356,1032,'Only approved values are stored. The uploader is notified if a document is not approved.')
text(x,y+420,'Open review -> screen 03. Approved records -> Materials (screen 04).',18)

x,y=panel(40,895,3,'Validate extracted information','Review queue')
text(x,y,'Review: vendor-coc-001.pdf',24,True)
text(x,y+36,'Material M-001  |  CoC  |  Status: Flagged  |  2 fields require attention',17)
box(x,y+73,380,289,'#f5f5f5');text(x+20,y+90,'Original PDF preview',20,True)
text(x+20,y+132,'Page 1 of 2   [Previous] [Next]',17)
box(x+30,y+177,320,125);text(x+48,y+197,'Source material / lot / property table',15)
text(x+48,y+231,'Highlighted source for selected field',15)
button(x,y+379,180,'Open source PDF')
table(x+404,y+73,628,['Field','Editable value','Review flag'],[['Material ID','M-001','--'],['Lot number','L-021','--'],['Tensile strength','[ 850 ] MPa','Low confidence'],['Elongation','[      ] %','Missing value']], [180,228,220])
text(x+404,y+281,'Select a value to inspect its source. Brackets = editable field.',15)
field(x+404,y+314,628,'Correction note','Explain correction when applicable')
button(x+404,y+400,160,'Save draft');button(x+580,y+400,225,'Re-extract / replace');button(x+822,y+400,210,'Approve record',True)
note(x,y+459,1032,'Approval feedback: resolve required flags first. Corrections and approvals record user and time.')

x,y=panel(1160,895,4,'Search and view material records','Materials')
text(x,y,'Materials',24,True)
field(x,y+44,300,'Material / lot','Search records')
field(x+322,y+44,225,'Vendor','All vendors')
field(x+569,y+44,225,'Source type','All / CoC / Test report')
button(x+816,y+69,100,'Search',True);button(x+932,y+69,100,'Reset')
text(x,y+121,'Approved records  |  2 matching records  |  [ ] Select records to compare',17)
table(x,y+155,1032,['Select','Material / lot','Vendor','Source type','Action'],[['[x]','M-001 / L-021','Vendor A','CoC','View details'],['[x]','M-001 / L-022','Vendor B','Test report','View details']], [80,300,220,210,222])
box(x,y+281,1032,130,'#f5f5f5');text(x+14,y+293,'Record details: M-001 / L-021  |  Approved',19,True)
text(x+14,y+328,'Properties: tensile strength 850 MPa; elongation 12%  |  Processing: view steps',16)
text(x+14,y+359,'Source: vendor-coc-001.pdf [Open PDF]  |  Review history [View]',16)
button(x,y+430,245,'Compare selected (2)',True)
text(x+270,y+442,'-> Analysis, screen 05',17)
text(x,y+490,'Empty state: No matching records. Change filters or reset your search.',16)

x,y=panel(40,1660,5,'Analysis results','Analysis')
text(x,y,'Compare material properties',24,True)
text(x,y+39,'Selection: M-001 / L-021 and M-001 / L-022  [Change selection]',17)
field(x,y+77,480,'Property','Tensile strength [select]')
field(x+512,y+77,520,'Analysis view','Compare / Historical trend / Property range')
table(x,y+165,1032,['Property','L-021 (CoC)','L-022 (Test report)','Units'],[['Tensile strength','850','870','MPa'],['Elongation','12','14','%']], [330,260,260,182])
box(x,y+302,1032,110,'#f5f5f5');text(x+18,y+317,'Property comparison preview',18,True)
text(x+18,y+351,'L-021',16);box(x+130,y+349,650,16,'#999999');text(x+800,y+349,'850 MPa',16)
text(x+18,y+382,'L-022',16);box(x+130,y+380,665,16,'#bbbbbb');text(x+815,y+380,'870 MPa',16)
note(x,y+432,1032,'Only approved, compatible values are compared. Missing/incompatible values show an explanation.')
text(x,y+486,'Specification limits: unavailable until supplied; no compliance conclusion is shown.',16)

text(1160,1660,'06  Navigation and interaction notes',27,True)
box(1160,1707,1080,640,'#f5f5f5')
for i,(a,b) in enumerate([
('01 Upload -> 02 Queue','Upload and process adds documents to the queue.'),
('02 Queue -> 03 Review','Open review loads extracted fields beside the original PDF.'),
('03 Review -> 04 Materials','Approval makes verified records available in Materials.'),
('04 Materials -> 05 Analysis','Select at least two compatible records, then Compare selected.'),
('Persistent navigation','Upload, Review queue, Materials and Analysis remain accessible.'),
('Feedback and access','Show loading, success, empty and error states; restrict actions by role.'),
('Design boundary','This wireframe specifies layout and behavior, not a final visual theme.')]):
    yy=1730+i*80;text(1184,yy,a,20,True);text(1184,yy+31,b,17)
text(40,2370,'Source: task #41, proposal sections 2–3, and existing use-case / ER design. All displayed records and values are examples.',18)
im.save(OUT.parent/'ui-wireframe.png')
for name,px,py in [('upload',40,130),('review-queue',1160,130),('validation',40,895),('materials',1160,895),('analysis',40,1660)]:
    im.crop((px-8,py-8,px+1088,py+695)).save(OUT/f'ui-wireframe-{name}.png')
svg.append('</svg>');(OUT/'ui-wireframe.svg').write_text('\n'.join(svg),encoding='utf-8')
print('Created ui-wireframe.png and editable ui-wireframe.svg')
