// Shared TypeScript contracts matching the Pydantic models returned by FastAPI.
export type Skill = { name: string; score: number; status: 'strong'|'partial'|'missing' };
export type Analysis = {
  id: string; matchScore: number; readiness: number; role: string; company: string;
  strongSkills: string[]; missingSkills: string[]; transferableSkills: string[]; skills: Skill[];
  insights: string[]; interviewFocus: string[];
  learningPlan: Array<{topic:string;priority:'High'|'Medium'|'Low';lessons:string[]}>;
};
export type Feedback = { score:number;technicalAccuracy:number;clarity:number;depth:number;relevance:number;strengths:string[];improvements:string[];suggestedAnswer:string };
