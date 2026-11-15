import assert from 'node:assert/strict';
import {referencePresentation,quickCue} from '../app/demo_static/reference-comparison.mjs';
const profile=(phone,height)=>({phone,family:'vowel',features:{tongue_height:height,tongue_region:'front',lip_shape:'unrounded'}});
const result={status:'uncertain',predicted_phone:'i',target_phone:'iː',details:{unresolved_reason:'notation_or_length'},
 articulation_feedback:{observed_reference:profile('i','high'),target_reference:profile('iː','high'),differences:[]}};
assert.equal(referencePresentation(result).kind,'shared');
assert.match(referencePresentation(result).note,/no length error is established/);
const changed=structuredClone(result);changed.predicted_phone='ɪ';changed.status='possible_difference';
changed.details={};changed.articulation_feedback.observed_reference=profile('ɪ','near-close');
changed.articulation_feedback.differences=[{adjustment:'Raise the tongue a little.'}];
assert.equal(referencePresentation(changed).kind,'contrast');
assert.equal(quickCue({word:'seat'},'iː',changed),'Raise the tongue a little.');
assert.equal(referencePresentation({...result,predicted_phone:null}).kind,'target');
assert.match(quickCue({word:'seat'},'iː',result),/comfortable pace/);
assert.doesNotMatch(quickCue({word:'seat'},'iː',result),/Raise|Lower/);
console.log('Shared reference, real contrasts and one-cue practice checks passed.');
