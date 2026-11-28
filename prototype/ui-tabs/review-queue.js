(function (root) {
    'use strict';

    const statuses = ['processing', 'failed', 'unsupported', 'pending', 'flagged', 'approved'];
    const demoDocuments = [
        {id:'DOC-001', filename:'vendor-coc-001.pdf', materialId:'MAT-AL-001', vendor:'Northstar Metals', status:'flagged', feedback:'2 fields need review', detail:'Extraction completed with two low-confidence fields.', progress:100},
        {id:'DOC-002', filename:'internal-report-002.pdf', materialId:'MAT-SS-204', vendor:'Internal test lab', status:'pending', feedback:'Awaiting approval', detail:'All required fields are present and ready for review.', progress:100},
        {id:'DOC-003', filename:'vendor-coc-003.pdf', materialId:'MAT-TI-090', vendor:'Apex Alloy Works', status:'processing', feedback:'Extracting fields', detail:'Page 3 of 5 analyzed. Identifying material and property fields.', progress:62},
        {id:'DOC-004', filename:'vendor-coc-004.pdf', materialId:'MAT-AL-118', vendor:'Northstar Metals', status:'failed', feedback:'PDF could not be read', detail:'The fixture simulates an unreadable or damaged PDF.', progress:0},
        {id:'DOC-005', filename:'vendor-coc-005.docx', materialId:'MAT-SS-310', vendor:'Apex Alloy Works', status:'unsupported', feedback:'Unsupported file type', detail:'Only PDF documents are supported by this prototype.', progress:0}
    ];

    function normalize(value) {
        return String(value || '').trim().toLocaleLowerCase();
    }

    function filterDocuments(documents, query, status) {
        const needle = normalize(query);
        const selectedStatus = normalize(status);
        if (selectedStatus === 'approved') return [];
        return documents.filter(document => {
            if (document.status === 'approved') return false;
            const matchesStatus = !selectedStatus || selectedStatus === 'all' || document.status === selectedStatus;
            const searchable = normalize(`${document.filename} ${document.materialId} ${document.vendor} ${document.id}`);
            return matchesStatus && (!needle || searchable.includes(needle));
        });
    }

    function createQueueStore(initialDocuments = demoDocuments) {
        const documents = initialDocuments.map(document => ({...document}));
        const busy = new Set();

        function findDocument(id) {
            const document = documents.find(candidate => candidate.id === String(id));
            if (!document) throw new Error('Document was not found in the illustrative queue.');
            return document;
        }

        function failIfRequested(options) {
            if (options.serviceError) throw new Error('Queue service unavailable (simulated).');
        }

        async function submitOnce(id, options, work) {
            const document = findDocument(id);
            if (busy.has(document.id)) return {accepted:false, duplicate:true, document};
            busy.add(document.id);
            try {
                await new Promise(resolve => setTimeout(resolve, options.delay || 0));
                failIfRequested(options);
                return await work(document);
            } finally {
                busy.delete(document.id);
            }
        }

        return {
            list(query = '', status = 'all') {
                return filterDocuments(documents, query, status).map(document => ({...document}));
            },
            get(id) {
                return {...findDocument(id)};
            },
            async refreshProcessing(id, options = {}) {
                return submitOnce(id, options, document => {
                    if (document.status !== 'processing') throw new Error('Only processing documents can be refreshed.');
                    document.status = options.failProcessing ? 'failed' : 'pending';
                    document.feedback = options.failProcessing ? 'Extraction failed; retry or replace the PDF' : 'Processing complete; awaiting review';
                    document.detail = options.failProcessing ? 'The simulated extraction could not read the document.' : 'Extraction completed. The record is not approved and must be reviewed.';
                    document.progress = options.failProcessing ? 0 : 100;
                    return {accepted:true, document:{...document}};
                });
            },
            async retryFailed(id, options = {}) {
                return submitOnce(id, options, document => {
                    if (document.status !== 'failed') throw new Error('Only failed documents can be retried.');
                    document.status = 'processing';
                    document.feedback = 'Retry accepted; extraction queued';
                    document.detail = 'A new processing attempt has been queued (simulated).';
                    document.progress = 0;
                    return {accepted:true, document:{...document}};
                });
            },
            async replaceFailed(id, file, options = {}) {
                if (!file || !/\.pdf$/i.test(file.name || '')) throw new Error('Choose a PDF file to replace this document.');
                return submitOnce(id, options, document => {
                    if (document.status !== 'failed') throw new Error('Only failed documents can be replaced.');
                    document.status = 'processing';
                    document.feedback = `Replacement accepted: ${file.name}`;
                    document.detail = 'The illustrative replacement has been queued for processing.';
                    document.progress = 0;
                    return {accepted:true, document:{...document}};
                });
            }
        };
    }

    const api = {statuses, demoDocuments, filterDocuments, createQueueStore};
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    root.ReviewQueue = api;
})(typeof window !== 'undefined' ? window : globalThis);
