"""AI Advisor for Flow State Analysis and Recommendations.

This module provides AI-powered analysis and recommendations for optimizing neural entrainment
and flow states using OpenAI's GPT-4 model. It processes brainwave data and provides
targeted recommendations for frequency adjustments and environmental triggers.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import json
from openai import OpenAI
import logging

@dataclass
class BrainwaveData:
    """Represents collected brainwave data across different frequency bands."""
    delta: List[float]
    theta: List[float]
    alpha: List[float]
    beta: List[float]
    gamma: List[float]

@dataclass
class FlowState:
    """Represents the analyzed flow state metrics and recommendations."""
    score: float
    alpha_quality: float
    theta_balance: float
    beta_suppression: float
    recommendations: List[str]

@dataclass
class FrequencyRecommendation:
    """Represents AI-generated frequency recommendations for neural entrainment."""
    base_freq: float
    beat_freq: float
    confidence: float
    reasoning: str

@dataclass
class FrequencyAdjustment:
    """Represents real-time adjustments to entrainment frequencies."""
    adjust_base_freq: float
    adjust_beat_freq: float
    confidence: float
    reasoning: str

@dataclass
class FlowTriggerSequence:
    """Represents a sequence of flow triggers with timing and intensity."""
    trigger: str
    timing: float
    intensity: float

@dataclass
class FlowEnvironment:
    """Represents environmental recommendations for optimal flow state."""
    lighting: str
    sound: str
    space: str

@dataclass
class FlowChallenge:
    """Represents a recommended challenge for maintaining flow state."""
    description: str
    difficulty: float
    duration: float

@dataclass
class FlowTriggerRecommendation:
    """Comprehensive flow state optimization recommendations."""
    triggers: List[str]
    sequence: List[FlowTriggerSequence]
    environment: FlowEnvironment
    challenges: List[FlowChallenge]

class AIAdvisor:
    """AI-powered advisor for flow state optimization and neural entrainment."""

    FLOW_STATE_PROMPT = """
    As a neurofeedback expert, analyze the following brainwave data and provide insights about the user's flow state:
    - Alpha waves (8-13 Hz): Associated with relaxed focus and learning
    - Theta waves (4-8 Hz): Associated with creativity and deep relaxation
    - Beta waves (13-30 Hz): Associated with active thinking and problem-solving
    - Delta waves (0.5-4 Hz): Associated with deep sleep and healing
    - Gamma waves (30-100 Hz): Associated with peak performance and insight

    Consider:
    1. Alpha/Theta ratio for optimal flow state
    2. Beta suppression for reduced analytical thinking
    3. Gamma bursts for moments of insight
    4. Overall wave pattern stability

    Current research suggests optimal flow states show:
    - Elevated alpha activity
    - Moderate theta activity
    - Reduced beta activity
    - Occasional gamma bursts
    
    Provide specific recommendations for improving or maintaining the current state.
    """

    def __init__(self, api_key: str):
        """Initialize the AI Advisor with OpenAI API key.

        Args:
            api_key: OpenAI API key for GPT-4 access
        """
        self.client = OpenAI(api_key=api_key)

    def calculate_metrics(self, data: BrainwaveData) -> Dict[str, float]:
        """Calculate key metrics from brainwave data.

        Args:
            data: BrainwaveData object containing wave measurements

        Returns:
            Dictionary containing calculated metrics
        """
        alpha_avg = float(np.mean(data.alpha))
        theta_avg = float(np.mean(data.theta))
        beta_avg = float(np.mean(data.beta))
        
        return {
            "alpha_avg": alpha_avg,
            "theta_avg": theta_avg,
            "beta_avg": beta_avg,
            "alpha_theta": alpha_avg / theta_avg if theta_avg > 0 else 0,
            "beta_suppress": 1 - (beta_avg / (alpha_avg + theta_avg)) if (alpha_avg + theta_avg) > 0 else 0
        }

    async def analyze_flow_state(self, data: BrainwaveData) -> FlowState:
        """Analyze brainwave data to assess flow state.

        Args:
            data: BrainwaveData object containing wave measurements

        Returns:
            FlowState object containing analysis and recommendations
        """
        metrics = self.calculate_metrics(data)
        
        prompt = f"""
        {self.FLOW_STATE_PROMPT}
        
        Current Metrics:
        - Alpha/Theta Ratio: {metrics['alpha_theta']:.2f}
        - Beta Suppression: {metrics['beta_suppress']:.2f}
        - Average Alpha: {metrics['alpha_avg']:.2f}
        - Average Theta: {metrics['theta_avg']:.2f}
        - Average Beta: {metrics['beta_avg']:.2f}
        
        Provide recommendations in JSON format:
        {{
            "flowScore": number between 0-1,
            "alphaQuality": number between 0-1,
            "thetaBalance": number between 0-1,
            "betaSuppression": number between 0-1,
            "recommendations": [string array of specific suggestions]
        }}
        """

        try:
            response = await self._get_completion(prompt, system_role="You are a neurofeedback expert specializing in flow states and peak performance.")
            result = json.loads(response)
            
            return FlowState(
                score=result.get("flowScore", 0),
                alpha_quality=result.get("alphaQuality", 0),
                theta_balance=result.get("thetaBalance", 0),
                beta_suppression=result.get("betaSuppression", 0),
                recommendations=result.get("recommendations", ["Unable to analyze flow state at this time."])
            )
        except Exception as e:
            logging.error(f"Error analyzing flow state: {str(e)}")
            return FlowState(
                score=0,
                alpha_quality=0,
                theta_balance=0,
                beta_suppression=0,
                recommendations=["Unable to analyze flow state at this time."]
            )

    async def get_frequency_recommendation(self, prompt: str) -> FrequencyRecommendation:
        """Get AI-powered frequency recommendations for neural entrainment.

        Args:
            prompt: Context and requirements for the recommendation

        Returns:
            FrequencyRecommendation object containing recommended frequencies
        """
        try:
            system_role = """You are a neurofeedback expert specializing in binaural beats and brainwave entrainment.
                Your recommendations should be based on the latest research in neuroscience and brainwave entrainment.
                Consider the user's current state, time of day, and historical response patterns.
                Provide specific, evidence-based frequency recommendations."""
                
            response = await self._get_completion(prompt, system_role=system_role)
            return FrequencyRecommendation(**json.loads(response))
        except Exception as e:
            logging.error(f"Error getting frequency recommendation: {str(e)}")
            raise

    async def get_frequency_adjustment(self, prompt: str) -> FrequencyAdjustment:
        """Get real-time frequency adjustments based on user response.

        Args:
            prompt: Current state and response data

        Returns:
            FrequencyAdjustment object containing recommended adjustments
        """
        try:
            system_role = """You are a neurofeedback expert specializing in real-time binaural beat optimization.
                Analyze brainwave metrics and suggest minor frequency adjustments to improve entrainment.
                Keep adjustments small and gradual to maintain stability.
                Consider the relationship between different frequency bands and their effects."""
                
            response = await self._get_completion(prompt, system_role=system_role)
            return FrequencyAdjustment(**json.loads(response))
        except Exception as e:
            logging.error(f"Error getting frequency adjustment: {str(e)}")
            raise

    async def get_flow_trigger_recommendation(self, prompt: str) -> FlowTriggerRecommendation:
        """Get comprehensive flow state trigger recommendations.

        Args:
            prompt: User context and requirements

        Returns:
            FlowTriggerRecommendation object containing optimization strategies
        """
        try:
            system_role = """You are a flow state expert from the Flow Research Collective.
                Your recommendations should be based on the latest flow research and neuroscience.
                Consider the user's current state, skill level, and environmental factors.
                Provide specific, actionable recommendations for achieving and maintaining flow state."""
                
            response = await self._get_completion(prompt, system_role=system_role)
            data = json.loads(response)
            
            # Convert nested structures to appropriate dataclasses
            sequence = [FlowTriggerSequence(**seq) for seq in data.get("sequence", [])]
            environment = FlowEnvironment(**data.get("environment", {}))
            challenges = [FlowChallenge(**challenge) for challenge in data.get("challenges", [])]
            
            return FlowTriggerRecommendation(
                triggers=data.get("triggers", []),
                sequence=sequence,
                environment=environment,
                challenges=challenges
            )
        except Exception as e:
            logging.error(f"Error getting flow trigger recommendation: {str(e)}")
            raise

    async def _get_completion(self, prompt: str, system_role: str) -> str:
        """Helper method to get GPT-4 completions.

        Args:
            prompt: User prompt
            system_role: System role description

        Returns:
            Model response as string
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error getting completion: {str(e)}")
            raise
