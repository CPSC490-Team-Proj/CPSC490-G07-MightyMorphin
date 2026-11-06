"""Package the existing SVG as per-screen vectors for Figma import."""
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

root = Path(__file__).parent
out = root / 'figma-wireframes'
out.mkdir(exist_ok=True)
tree = ET.parse(root / 'ui-wireframe.svg')
items = list(tree.getroot())[1:]
screens = [('01-upload',40,130),('02-review-queue',1160,130),('03-validation',40,895),('04-materials',1160,895),('05-analysis',40,1660)]
data = []
for name,x,y in screens:
    nodes = []
    svg = ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width='1096',height='703',viewBox='0 0 1096 703')
    for element in items:
        ex,ey = float(element.get('x','0')),float(element.get('y','0'))
        if not (x-8 <= ex < x+1088 and y-8 <= ey < y+695):
            continue
        tag = element.tag.split('}')[-1]
        if tag not in ('rect','text'):
            raise ValueError(tag)
        attrs = dict(element.attrib)
        attrs['x'],attrs['y'] = str(ex-x+8),str(ey-y+8)
        el = ET.SubElement(svg,tag,attrs)
        el.text = element.text
        nodes.append(dict(type=tag,attrs=attrs,text=element.text or ''))
    ET.ElementTree(svg).write(out/f'{name}.svg',encoding='utf-8',xml_declaration=True)
    data.append(dict(name=name,nodes=nodes))

for p in out.glob('*.svg'):
    ET.parse(p)
with zipfile.ZipFile(root/'ui-wireframe-figma.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.glob('*.svg')):
        z.write(p,'figma-wireframes/'+p.name)
print('Prepared five SVG screens for Figma import.')
