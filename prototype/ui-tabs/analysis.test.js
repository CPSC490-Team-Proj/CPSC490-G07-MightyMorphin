const test=require('node:test');
const assert=require('node:assert/strict');
const {analyze,demoRecords}=require('./analysis.js');
test('comparison returns approved values at stored precision',()=>{const r=analyze(demoRecords,['1','2'],'strength','compare');assert.equal(r.empty,false);assert.deepEqual(r.values.map(x=>x.value),[850.125,870.25]);assert.equal(r.unit,'MPa');});
test('excludes unapproved, missing and incompatible records with reasons',()=>{const r=analyze(demoRecords,['1','2','3','4','5','99'],'strength','compare');assert.equal(r.values.length,2);assert.equal(r.warnings.length,4);assert.match(r.warnings.join(' '),/incompatible unit ksi/);assert.match(r.warnings.join(' '),/not approved/);});
test('empty selection and insufficient comparison are explicit',()=>{assert.equal(analyze(demoRecords,[],'strength','compare').empty,true);assert.equal(analyze(demoRecords,['1'],'strength','compare').empty,true);});
test('range supports one value and returns exact extrema',()=>{const r=analyze(demoRecords,['2','1'],'strength','range');assert.equal(r.min,850.125);assert.equal(r.max,870.25);assert.equal(analyze(demoRecords,['1'],'strength','range').empty,false);});
test('trend sorts by date and excludes undated points',()=>{const records=[...demoRecords,{...demoRecords[0],id:'6',date:null}];const r=analyze(records,['2','6','1'],'strength','trend');assert.deepEqual(r.values.map(x=>x.id),['1','2']);assert.match(r.warnings[0],/date/);});
test('deduplicates selected IDs and rejects unsupported requests',()=>{assert.equal(analyze(demoRecords,['1','1'],'strength','range').values.length,1);assert.throws(()=>analyze(demoRecords,['1'],'unknown','compare'));});
