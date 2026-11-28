const test=require('node:test');
const assert=require('node:assert/strict');
const {createQueueStore,demoDocuments,filterDocuments,statuses}=require('./review-queue.js');

test('fixture statuses cover queue states without approved rows',()=>{
    assert.deepEqual(statuses,['processing','failed','unsupported','pending','flagged','approved']);
    assert.deepEqual(new Set(demoDocuments.map(document=>document.status)),new Set(['processing','failed','unsupported','pending','flagged']));
});

test('search matches filename, material ID, vendor and document ID case-insensitively',()=>{
    assert.equal(filterDocuments(demoDocuments,'NORTHSTAR','all').length,2);
    assert.equal(filterDocuments(demoDocuments,'mat-ti-090','all')[0].id,'DOC-003');
    assert.equal(filterDocuments(demoDocuments,'doc-001','all')[0].id,'DOC-001');
});

test('status filter handles each queue status and approved stays outside the queue',()=>{
    for(const status of statuses.slice(0,-1)) assert.ok(filterDocuments(demoDocuments,'',status).every(document=>document.status===status));
    assert.deepEqual(filterDocuments(demoDocuments,'','approved'),[]);
});

test('processing refresh transitions to pending but never approves the record',async()=>{
    const store=createQueueStore();
    const result=await store.refreshProcessing('DOC-003');
    assert.equal(result.document.status,'pending');
    assert.equal(result.document.progress,100);
    assert.match(result.document.feedback,/awaiting review/);
});

test('processing failure becomes failed and can be retried',async()=>{
    const store=createQueueStore();
    const failed=await store.refreshProcessing('DOC-003',{failProcessing:true});
    assert.equal(failed.document.status,'failed');
    const retried=await store.retryFailed('DOC-003');
    assert.equal(retried.document.status,'processing');
});

test('failed-document retry rejects service errors and duplicate requests',async()=>{
    const store=createQueueStore();
    await assert.rejects(store.retryFailed('DOC-004',{serviceError:true}),/unavailable/);
    const pending=store.retryFailed('DOC-004',{delay:10});
    const duplicate=await store.retryFailed('DOC-004');
    assert.equal(duplicate.accepted,false);
    assert.equal(duplicate.duplicate,true);
    assert.equal((await pending).accepted,true);
});

test('replacement requires a PDF and records successful replacement feedback',async()=>{
    const store=createQueueStore();
    await assert.rejects(store.replaceFailed('DOC-004',{name:'replacement.docx'}),/PDF/);
    const result=await store.replaceFailed('DOC-004',{name:'replacement.pdf'});
    assert.equal(result.document.status,'processing');
    assert.match(result.document.feedback,/replacement.pdf/);
});

test('service errors do not mutate a failed record',async()=>{
    const store=createQueueStore();
    await assert.rejects(store.retryFailed('DOC-004',{serviceError:true}),/unavailable/);
    assert.equal(store.get('DOC-004').status,'failed');
});
