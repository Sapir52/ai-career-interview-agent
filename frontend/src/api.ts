// Typed HTTP client for communication with the Python FastAPI backend.
import type { Analysis, Feedback } from './types';
// Local development targets FastAPI on port 8000; AWS deployments override VITE_API_URL.
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
async function req(path:string, options?:RequestInit){
  // Centralize JSON headers and convert non-2xx responses into JavaScript errors.
  const r=await fetch(`${API}${path}`,{headers:{'content-type':'application/json'},...options});
  if(!r.ok) throw new Error(await r.text()); return r.json();
}
export const analyze = (cv:string,job:string)=>req('/analyze',{method:'POST',body:JSON.stringify({cv,job})}) as Promise<Analysis>;
export const evaluate = (question:string,answer:string,analysis?:Analysis)=>req('/interview/evaluate',{method:'POST',body:JSON.stringify({question,answer,analysis})}) as Promise<{feedback:Feedback;followUp:string}>;
export const extractCv = (filename:string,contentBase64:string)=>req('/cv/extract',{method:'POST',body:JSON.stringify({filename,contentBase64})}) as Promise<{text:string;s3Key?:string|null}>;
