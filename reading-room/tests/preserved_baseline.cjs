'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
// Two approved presentation-only files use exact reviewed replacements.
// All other old files are read unchanged; navigation/storage/core are never waived.
function preservedBytes(root,file){
  const contract=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/approved-ui-changes.json'),'utf8'));
  assert.deepEqual(contract.allowed_files,['dist/app.js','dist/style.css']);
  assert.deepEqual(Object.keys(contract.files),contract.allowed_files);
  if(!contract.allowed_files.includes(file))return fs.readFileSync(path.join(root,file));
  const entry=contract.files[file];assert.equal(entry.fixture,file==='dist/app.js'?'fourteen-app.js':'fourteen-style.css');
  const baseline=fs.readFileSync(path.join(__dirname,'fixtures',entry.fixture));let expected=baseline.toString('utf8');
  assert.equal(entry.changes.length,file==='dist/app.js'?5:1);
  for(const change of entry.changes){
    assert(change.before&&change.after);assert.equal(expected.split(change.before).length,2,'UI patch has one exact location');
    expected=expected.replace(change.before,change.after);
  }
  assert.equal(fs.readFileSync(path.join(root,file),'utf8'),expected,'Only exact source-label, status and marker UI edits are allowed');
  return baseline;
}
module.exports={preservedBytes};
