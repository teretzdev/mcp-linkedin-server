#!/usr/bin/env python3
"""
AI Easy Apply Service
Provides intelligent answer generation for LinkedIn Easy Apply questions using Gemini API
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ApplicantProfile:
    """Applicant profile data for AI context"""
    name: str
    email: str
    phone: str
    location: str
    experience_years: int
    skills: List[str]
    education: str
    languages: List[str]
    work_authorization: str
    salary_expectation: str
    availability: str
    current_position: str = ""
    target_roles: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

@dataclass
class JobContext:
    """Job context for AI analysis"""
    title: str
    company: str
    location: str
    salary_range: str
    description: str
    requirements: List[str]
    responsibilities: List[str]
    job_type: str
    remote: bool

@dataclass
class ApplicationQuestion:
    """Application question structure"""
    id: str
    question: str
    type: str  # 'text', 'select', 'textarea', 'number', 'date'
    required: bool
    category: str  # 'experience', 'authorization', 'compensation', 'availability', 'skills'
    options: List[str] = None
    max_length: int = None

class AIEasyApplyService:
    """AI-powered Easy Apply answer generation service"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.gemini_model = None
        self.setup_gemini()
        
    def setup_gemini(self):
        """Setup Gemini API connection"""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini not available. Install with: pip install google-generativeai")
            return
            
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
            return
            
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup Gemini: {e}")
            self.gemini_model = None
    
    async def generate_answer(
        self, 
        question: ApplicationQuestion, 
        applicant_profile: ApplicantProfile, 
        job_context: JobContext,
        previous_answers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate intelligent answer for application question"""
        
        if not self.gemini_model:
            return {
                "success": False,
                "error": "Gemini API not available",
                "fallback_answer": self._generate_fallback_answer(question, applicant_profile)
            }
        
        try:
            # Build context-aware prompt
            prompt = self._build_prompt(question, applicant_profile, job_context, previous_answers)
            
            # Generate response
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            # Parse and validate response
            answer = self._parse_ai_response(response.text, question)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(answer, question, job_context)
            
            return {
                "success": True,
                "answer": answer,
                "suggestions": suggestions,
                "confidence": self._calculate_confidence(answer, question),
                "reasoning": self._extract_reasoning(response.text)
            }
            
        except Exception as e:
            logger.error(f"AI answer generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_answer": self._generate_fallback_answer(question, applicant_profile)
            }
    
    def _build_prompt(
        self, 
        question: ApplicationQuestion, 
        applicant_profile: ApplicantProfile, 
        job_context: JobContext,
        previous_answers: Optional[Dict[str, str]] = None
    ) -> str:
        """Build context-aware prompt for AI"""
        
        prompt = f"""
You are an AI assistant helping a job applicant answer LinkedIn Easy Apply questions intelligently and professionally.

JOB CONTEXT:
- Position: {job_context.title}
- Company: {job_context.company}
- Location: {job_context.location}
- Salary Range: {job_context.salary_range}
- Job Type: {job_context.job_type}
- Remote: {'Yes' if job_context.remote else 'No'}
- Requirements: {', '.join(job_context.requirements)}
- Responsibilities: {', '.join(job_context.responsibilities)}

APPLICANT PROFILE:
- Name: {applicant_profile.name}
- Experience: {applicant_profile.experience_years} years
- Current Position: {applicant_profile.current_position}
- Skills: {', '.join(applicant_profile.skills)}
- Education: {applicant_profile.education}
- Work Authorization: {applicant_profile.work_authorization}
- Salary Expectation: {applicant_profile.salary_expectation}
- Availability: {applicant_profile.availability}
- Languages: {', '.join(applicant_profile.languages)}
- Target Roles: {', '.join(applicant_profile.target_roles or [])}
- Key Achievements: {', '.join(applicant_profile.achievements or [])}

QUESTION TO ANSWER:
- Question: {question.question}
- Type: {question.type}
- Category: {question.category}
- Required: {question.required}
- Options: {question.options if question.options else 'Free text'}

PREVIOUS ANSWERS (for context):
{self._format_previous_answers(previous_answers) if previous_answers else 'None'}

INSTRUCTIONS:
1. Provide a professional, honest, and compelling answer
2. Tailor the response to the specific job and company
3. Use specific examples and metrics when possible
4. Keep the tone confident but not arrogant
5. Ensure the answer aligns with the applicant's profile
6. If it's a select question, choose the most appropriate option
7. If it's a text/textarea, provide a concise but detailed response

Please provide your answer in a clear, professional format that would impress a hiring manager.
"""
        return prompt
    
    def _format_previous_answers(self, previous_answers: Dict[str, str]) -> str:
        """Format previous answers for context"""
        if not previous_answers:
            return "None"
        
        formatted = []
        for q_id, answer in previous_answers.items():
            formatted.append(f"- {q_id}: {answer}")
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response: str, question: ApplicationQuestion) -> str:
        """Parse and clean AI response"""
        # Remove any markdown formatting
        cleaned = response.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('```')[1]
        if cleaned.startswith('**') and cleaned.endswith('**'):
            cleaned = cleaned[2:-2]
        
        # For select questions, try to match with options
        if question.type == 'select' and question.options:
            for option in question.options:
                if option.lower() in cleaned.lower():
                    return option
            # If no match found, return the first option as fallback
            return question.options[0]
        
        # For text questions, limit length if specified
        if question.max_length and len(cleaned) > question.max_length:
            cleaned = cleaned[:question.max_length-3] + "..."
        
        return cleaned
    
    def _generate_suggestions(self, answer: str, question: ApplicationQuestion, job_context: JobContext) -> List[Dict[str, str]]:
        """Generate improvement suggestions for the answer"""
        suggestions = []
        
        # Check for common improvement areas
        if question.category == 'experience':
            if 'years' in question.question.lower() and not any(char.isdigit() for char in answer):
                suggestions.append({
                    "type": "improvement",
                    "message": "Consider adding specific years of experience to make your answer more concrete."
                })
            
            if 'project' in question.question.lower() and len(answer) < 100:
                suggestions.append({
                    "type": "improvement", 
                    "message": "Add more details about the project scope, technologies used, and outcomes achieved."
                })
        
        elif question.category == 'compensation':
            if 'salary' in question.question.lower() and not any(char.isdigit() for char in answer):
                suggestions.append({
                    "type": "improvement",
                    "message": "Consider providing a specific salary range that aligns with the job posting."
                })
        
        # Add positive feedback for good answers
        if len(answer) > 50 and any(keyword in answer.lower() for keyword in ['experience', 'skills', 'achieved', 'developed']):
            suggestions.append({
                "type": "tip",
                "message": "Great answer! It shows relevant experience and achievements."
            })
        
        return suggestions
    
    def _calculate_confidence(self, answer: str, question: ApplicationQuestion) -> float:
        """Calculate confidence score for the generated answer"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for longer, more detailed answers
        if len(answer) > 100:
            confidence += 0.2
        
        # Increase confidence for answers with specific details
        if any(char.isdigit() for char in answer):
            confidence += 0.1
        
        # Increase confidence for answers with action verbs
        action_verbs = ['developed', 'implemented', 'managed', 'led', 'created', 'built', 'achieved']
        if any(verb in answer.lower() for verb in action_verbs):
            confidence += 0.1
        
        # Decrease confidence for very short answers
        if len(answer) < 20:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from AI response if available"""
        # Look for reasoning patterns in the response
        reasoning_indicators = [
            "because", "since", "as", "given that", "considering",
            "this shows", "this demonstrates", "this indicates"
        ]
        
        for indicator in reasoning_indicators:
            if indicator in response.lower():
                # Extract the sentence containing the reasoning
                sentences = response.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()
        
        return "AI-generated response based on applicant profile and job requirements."
    
    def _generate_fallback_answer(self, question: ApplicationQuestion, applicant_profile: ApplicantProfile) -> str:
        """Generate fallback answer when AI is not available"""
        
        if question.type == 'select' and question.options:
            # Return the most appropriate option based on category
            if question.category == 'authorization':
                return applicant_profile.work_authorization
            elif question.category == 'availability':
                return applicant_profile.availability
            else:
                return question.options[0] if question.options else ""
        
        elif question.category == 'experience':
            if 'years' in question.question.lower():
                return f"{applicant_profile.experience_years} years"
            elif 'project' in question.question.lower():
                return f"I led the development of a scalable web application using {', '.join(applicant_profile.skills[:3])}. The project improved user engagement by 40% and reduced load times by 60%."
            else:
                return f"I have {applicant_profile.experience_years} years of experience in {applicant_profile.current_position or 'software development'}."
        
        elif question.category == 'compensation':
            return applicant_profile.salary_expectation
        
        elif question.category == 'skills':
            return f"I am proficient in {', '.join(applicant_profile.skills[:5])} and have experience with modern development practices."
        
        else:
            return f"I am excited about this opportunity and believe my skills and experience make me a great fit for this role."
    
    async def analyze_job_fit(self, applicant_profile: ApplicantProfile, job_context: JobContext) -> Dict[str, Any]:
        """Analyze how well the applicant fits the job"""
        
        if not self.gemini_model:
            return {
                "success": False,
                "error": "Gemini API not available",
                "fit_score": 0.5
            }
        
        try:
            prompt = f"""
Analyze the fit between this applicant and job posting:

APPLICANT:
- Experience: {applicant_profile.experience_years} years
- Skills: {', '.join(applicant_profile.skills)}
- Education: {applicant_profile.education}
- Target Roles: {', '.join(applicant_profile.target_roles or [])}

JOB:
- Title: {job_context.title}
- Company: {job_context.company}
- Requirements: {', '.join(job_context.requirements)}
- Responsibilities: {', '.join(job_context.responsibilities)}

Provide a fit analysis with:
1. Fit score (0-100)
2. Key strengths
3. Potential concerns
4. Recommendations for application
"""
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            # Extract fit score from response
            fit_score = self._extract_fit_score(response.text)
            
            return {
                "success": True,
                "fit_score": fit_score,
                "analysis": response.text,
                "strengths": self._extract_strengths(response.text),
                "concerns": self._extract_concerns(response.text),
                "recommendations": self._extract_recommendations(response.text)
            }
            
        except Exception as e:
            logger.error(f"Job fit analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fit_score": 0.5
            }
    
    def _extract_fit_score(self, analysis: str) -> float:
        """Extract fit score from analysis text"""
        try:
            # Look for percentage patterns
            import re
            percentages = re.findall(r'(\d+)%', analysis)
            if percentages:
                return float(percentages[0]) / 100.0
            
            # Look for score patterns
            scores = re.findall(r'score[:\s]*(\d+)', analysis.lower())
            if scores:
                return float(scores[0]) / 100.0
            
            # Look for fit patterns
            fits = re.findall(r'fit[:\s]*(\d+)', analysis.lower())
            if fits:
                return float(fits[0]) / 100.0
            
        except:
            pass
        
        return 0.5  # Default score
    
    def _extract_strengths(self, analysis: str) -> List[str]:
        """Extract strengths from analysis"""
        strengths = []
        lines = analysis.split('\n')
        in_strengths = False
        
        for line in lines:
            if 'strength' in line.lower() or 'strong' in line.lower():
                in_strengths = True
                continue
            elif in_strengths and line.strip():
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    strengths.append(line.strip()[1:].strip())
                elif 'concern' in line.lower() or 'weakness' in line.lower():
                    break
        
        return strengths
    
    def _extract_concerns(self, analysis: str) -> List[str]:
        """Extract concerns from analysis"""
        concerns = []
        lines = analysis.split('\n')
        in_concerns = False
        
        for line in lines:
            if 'concern' in line.lower() or 'weakness' in line.lower():
                in_concerns = True
                continue
            elif in_concerns and line.strip():
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    concerns.append(line.strip()[1:].strip())
                elif 'recommendation' in line.lower():
                    break
        
        return concerns
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from analysis"""
        recommendations = []
        lines = analysis.split('\n')
        in_recommendations = False
        
        for line in lines:
            if 'recommendation' in line.lower() or 'suggest' in line.lower():
                in_recommendations = True
                continue
            elif in_recommendations and line.strip():
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    recommendations.append(line.strip()[1:].strip())
        
        return recommendations

# Global service instance
_ai_service = None

def get_ai_service(gemini_api_key: Optional[str] = None) -> AIEasyApplyService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIEasyApplyService(gemini_api_key)
    return _ai_service

# Example usage
if __name__ == "__main__":
    # Test the service
    async def test_service():
        service = get_ai_service()
        
        # Create test data
        profile = ApplicantProfile(
            name="Sarah Chen",
            email="sarah.chen@email.com",
            phone="+1 (555) 123-4567",
            location="San Francisco, CA",
            experience_years=4,
            skills=["React", "JavaScript", "Node.js", "Python", "AWS"],
            education="Bachelor of Science in Computer Science",
            languages=["English", "Spanish"],
            work_authorization="US Citizen",
            salary_expectation="$120,000 - $140,000",
            availability="2 weeks notice",
            current_position="Senior Frontend Developer",
            target_roles=["Software Engineer", "Full Stack Developer"],
            achievements=["Led team of 5 developers", "Improved app performance by 60%"]
        )
        
        job = JobContext(
            title="Senior React Developer",
            company="TechCorp Inc.",
            location="San Francisco, CA",
            salary_range="$120,000 - $150,000",
            description="We are looking for a Senior React Developer...",
            requirements=["React", "JavaScript", "TypeScript", "5+ years experience"],
            responsibilities=["Build scalable applications", "Lead development team"],
            job_type="Full-time",
            remote=True
        )
        
        question = ApplicationQuestion(
            id="1",
            question="How many years of experience do you have with React?",
            type="text",
            required=True,
            category="experience"
        )
        
        # Test answer generation
        result = await service.generate_answer(question, profile, job)
        print("Answer Generation Result:")
        print(json.dumps(result, indent=2))
        
        # Test job fit analysis
        fit_result = await service.analyze_job_fit(profile, job)
        print("\nJob Fit Analysis Result:")
        print(json.dumps(fit_result, indent=2))
    
    asyncio.run(test_service()) 