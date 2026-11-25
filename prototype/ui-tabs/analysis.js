(function (root) {
    'use strict';
    const demoRecords = [
        {id:'1', name:'Material A / Lot A', status:'Approved', date:'2026-10-01', properties:{strength:{value:850.125,unit:'MPa'},elongation:{value:12,unit:'%'}}},
        {id:'2', name:'Material A / Lot B', status:'Approved', date:'2026-11-01', properties:{strength:{value:870.25,unit:'MPa'},elongation:{value:14,unit:'%'}}},
        {id:'3', name:'Material A / Lot C', status:'Approved', date:'2026-11-03', properties:{strength:{value:125,unit:'ksi'}}},
        {id:'4', name:'Material A / Lot D', status:'Approved', date:'2026-11-10', properties:{elongation:{value:13,unit:'%'}}},
        {id:'5', name:'Material A / Lot E', status:'Flagged', date:'2026-11-12', properties:{strength:{value:999,unit:'MPa'}}}
    ];
    const properties = {strength:{label:'Tensile strength',unit:'MPa'},elongation:{label:'Elongation',unit:'%'}};
    function analyze(records, ids, property, view) {
        if (!properties[property] || !['compare','trend','range'].includes(view)) throw Error('Unsupported property or view.');
        const warnings=[], values=[], selected=[...new Set(ids.map(String))];
        for (const id of selected) {
            const r=records.find(r=>String(r.id)===id);
            if (!r) {warnings.push(`Record ${id}: not found.`);continue;}
            if (r.status!=='Approved') {warnings.push(`${r.name}: excluded because it is not approved.`);continue;}
            const p=r.properties[property];
            if (!p || typeof p.value!=='number' || !Number.isFinite(p.value)) {warnings.push(`${r.name}: missing or invalid property value.`);continue;}
            if (p.unit!==properties[property].unit) {warnings.push(`${r.name}: incompatible unit ${p.unit}; no automatic conversion.`);continue;}
            if (view==='trend' && (!/^\d{4}-\d{2}-\d{2}$/.test(r.date||'') || !Number.isFinite(Date.parse(r.date)))) {warnings.push(`${r.name}: missing or invalid date for trend.`);continue;}
            values.push({id:r.id,name:r.name,date:r.date,value:p.value,unit:p.unit});
        }
        if (view==='trend') values.sort((a,b)=>a.date.localeCompare(b.date));
        const minimum=view==='range'?1:2;
        return {values,warnings,empty:values.length<minimum,minimum,unit:properties[property].unit,
            min:values.length?Math.min(...values.map(x=>x.value)):null,max:values.length?Math.max(...values.map(x=>x.value)):null};
    }
    const api={analyze,demoRecords,properties};
    if (typeof module!=='undefined' && module.exports) module.exports=api;
    root.MaterialAnalysis=api;
})(typeof window!=='undefined'?window:globalThis);
