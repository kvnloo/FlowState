"""Research and Activity Optimization System.

This module maintains an expanding knowledge base of flow-related research
and provides personalized activity recommendations based on EEG data,
recovery metrics, and activity tracking.

Key Features:
    - Automated research aggregation
    - Activity-recovery correlation analysis
    - Personalized intervention recommendations
    - Continuous knowledge base expansion
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
import json
import aiohttp
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from biometric.whoop_client import WhoopClient
from flow.recovery_system import RecoveryAndIntegrationSystem

@dataclass
class ResearchSource:
    """Container for research source information."""
    url: str
    title: str
    abstract: str
    keywords: List[str]
    publication_date: datetime
    relevance_score: float
    citations: int
    category: str
    last_updated: datetime

@dataclass
class Activity:
    """Container for activity information."""
    name: str
    duration: timedelta
    intensity: float  # 0-1 scale
    category: str
    recovery_impact: float  # -1 to 1 scale
    neuroplasticity_boost: float  # 0-1 scale
    eeg_compatibility: float  # 0-1 scale
    recommended_time: str  # Time of day
    contraindications: List[str]

class ResearchSystem:
    """Manages research aggregation and activity optimization."""
    
    def __init__(self,
                 recovery_system: RecoveryAndIntegrationSystem,
                 whoop_client: WhoopClient,
                 db_path: str = "research_db.json"):
        """Initialize the research system.
        
        Args:
            recovery_system: Recovery tracking and optimization
            whoop_client: Activity and recovery tracking
            db_path: Path to research database file
        """
        self.recovery_system = recovery_system
        self.whoop_client = whoop_client
        self.db_path = db_path
        
        # Research sources
        self.sources: Dict[str, ResearchSource] = {}
        self.activities: Dict[str, Activity] = {}
        self.keywords: Set[str] = set()
        
        # API configurations
        self.api_configs = {
            'arxiv': {
                'base_url': 'http://export.arxiv.org/api/query',
                'categories': ['q-bio.NC', 'cs.HC', 'stat.ML']
            },
            'pubmed': {
                'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
                'categories': ['neuroscience', 'cognitive enhancement', 'flow state']
            },
            'perplexity': {
                'base_url': 'https://api.perplexity.ai/search',
                'categories': ['flow state', 'neural entrainment', 'cognitive optimization']
            }
        }
        
        # Analysis parameters
        self.relevance_threshold = 0.7
        self.update_interval = timedelta(days=1)
        self.max_sources_per_update = 100
        
        # Load existing database
        self._load_database()
        
    async def update_research(self):
        """Update research database with new sources."""
        tasks = []
        for source, config in self.api_configs.items():
            for category in config['categories']:
                tasks.append(self._fetch_research(source, category))
                
        results = await asyncio.gather(*tasks)
        new_sources = [source for result in results for source in result]
        
        # Filter and add relevant sources
        for source in new_sources:
            if self._compute_relevance(source) >= self.relevance_threshold:
                self.sources[source.url] = source
                self.keywords.update(source.keywords)
                
        # Update database
        self._save_database()
        
        # Update activity recommendations based on new research
        await self._update_activity_recommendations()
        
    async def get_activity_recommendations(self, eeg_data: np.ndarray) -> List[Activity]:
        """Get personalized activity recommendations based on current state.
        
        Args:
            eeg_data: Current EEG readings
            
        Returns:
            List of recommended activities sorted by relevance
        """
        # Get current recovery metrics
        recovery_metrics = await self.recovery_system.compute_recovery_metrics()
        
        # Get recent activity data
        activity_data = await self.whoop_client.get_activities(days=7)
        
        # Analyze EEG patterns for optimal activities
        eeg_profile = self._analyze_eeg_patterns(eeg_data)
        
        # Score activities based on current state
        scored_activities = []
        for activity in self.activities.values():
            score = self._compute_activity_score(
                activity=activity,
                recovery_metrics=recovery_metrics,
                eeg_profile=eeg_profile,
                recent_activities=activity_data
            )
            scored_activities.append((score, activity))
            
        # Sort by score and return top activities
        scored_activities.sort(reverse=True)
        return [activity for _, activity in scored_activities[:5]]
        
    async def track_activity_impact(self, activity_name: str):
        """Track the impact of an activity on recovery and performance.
        
        Args:
            activity_name: Name of the activity to track
        """
        if activity_name not in self.activities:
            return
            
        # Get pre-activity metrics
        pre_recovery = await self.recovery_system.compute_recovery_metrics()
        pre_hrv = await self.whoop_client.get_hrv()
        
        # Store activity start time
        start_time = datetime.now()
        
        # Wait for activity duration
        await asyncio.sleep(self.activities[activity_name].duration.total_seconds())
        
        # Get post-activity metrics
        post_recovery = await self.recovery_system.compute_recovery_metrics()
        post_hrv = await self.whoop_client.get_hrv()
        
        # Update activity impact metrics
        self._update_activity_impact(
            activity_name=activity_name,
            pre_recovery=pre_recovery,
            post_recovery=post_recovery,
            pre_hrv=pre_hrv,
            post_hrv=post_hrv,
            duration=datetime.now() - start_time
        )
        
    async def _fetch_research(self, source: str, category: str) -> List[ResearchSource]:
        """Fetch research from a specific source and category."""
        async with aiohttp.ClientSession() as session:
            if source == 'arxiv':
                return await self._fetch_arxiv(session, category)
            elif source == 'pubmed':
                return await self._fetch_pubmed(session, category)
            elif source == 'perplexity':
                return await self._fetch_perplexity(session, category)
        return []
        
    def _compute_relevance(self, source: ResearchSource) -> float:
        """Compute relevance score for a research source."""
        # Use TF-IDF to compare with existing relevant sources
        if not self.sources:
            return 0.8  # Default score for first sources
            
        vectorizer = TfidfVectorizer()
        corpus = [s.abstract for s in self.sources.values()]
        corpus.append(source.abstract)
        
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
        
        return float(np.mean(similarities))
        
    def _analyze_eeg_patterns(self, eeg_data: np.ndarray) -> Dict[str, float]:
        """Analyze EEG patterns for activity compatibility."""
        # Extract relevant EEG features
        theta_power = np.mean(self._bandpower(eeg_data, 4, 8))
        alpha_power = np.mean(self._bandpower(eeg_data, 8, 13))
        beta_power = np.mean(self._bandpower(eeg_data, 13, 30))
        gamma_power = np.mean(self._bandpower(eeg_data, 30, 50))
        
        return {
            'theta_power': theta_power,
            'alpha_power': alpha_power,
            'beta_power': beta_power,
            'gamma_power': gamma_power,
            'alpha_theta_ratio': alpha_power / theta_power if theta_power > 0 else 1.0
        }
        
    def _compute_activity_score(self,
                             activity: Activity,
                             recovery_metrics,
                             eeg_profile: Dict[str, float],
                             recent_activities) -> float:
        """Compute score for an activity based on current state."""
        # Base score from recovery impact
        base_score = activity.recovery_impact
        
        # Adjust for current recovery state
        if recovery_metrics.cognitive_recovery < 0.3:
            base_score *= activity.neuroplasticity_boost
            
        # Adjust for EEG compatibility
        eeg_compatibility = self._compute_eeg_compatibility(
            activity=activity,
            eeg_profile=eeg_profile
        )
        base_score *= (0.5 + 0.5 * eeg_compatibility)
        
        # Penalize recently performed activities
        if self._was_recent_activity(activity.name, recent_activities):
            base_score *= 0.7
            
        return float(np.clip(base_score, 0, 1))
        
    def _compute_eeg_compatibility(self,
                                activity: Activity,
                                eeg_profile: Dict[str, float]) -> float:
        """Compute compatibility between activity and current EEG state."""
        if activity.category == 'meditation':
            # Prefer high alpha/theta ratio for meditation
            return 1.0 - abs(0.8 - eeg_profile['alpha_theta_ratio'])
        elif activity.category == 'exercise':
            # Prefer moderate beta for exercise
            return 1.0 - abs(0.6 - eeg_profile['beta_power'])
        elif activity.category == 'learning':
            # Prefer high theta and gamma for learning
            return (eeg_profile['theta_power'] + eeg_profile['gamma_power']) / 2
            
        return activity.eeg_compatibility
        
    def _bandpower(self, data: np.ndarray, fmin: float, fmax: float) -> np.ndarray:
        """Compute bandpower in a specific frequency range."""
        # Implement band power calculation
        # This is a placeholder - actual implementation would use proper DSP
        return np.array([0.5])
        
    def _was_recent_activity(self, activity_name: str, recent_activities) -> bool:
        """Check if activity was performed recently."""
        for activity in recent_activities:
            if activity['name'] == activity_name:
                return True
        return False
        
    def _update_activity_impact(self,
                             activity_name: str,
                             pre_recovery,
                             post_recovery,
                             pre_hrv: np.ndarray,
                             post_hrv: np.ndarray,
                             duration: timedelta):
        """Update activity impact metrics based on measurements."""
        activity = self.activities[activity_name]
        
        # Compute recovery impact
        recovery_change = (post_recovery.cognitive_recovery - 
                         pre_recovery.cognitive_recovery)
        
        # Compute HRV impact
        hrv_change = np.mean(post_hrv) - np.mean(pre_hrv)
        
        # Update activity metrics with exponential moving average
        alpha = 0.3  # Learning rate
        activity.recovery_impact = (1 - alpha) * activity.recovery_impact + \
                                 alpha * np.clip(recovery_change, -1, 1)
                                 
        # Update duration if significantly different
        if abs((duration - activity.duration).total_seconds()) > 300:  # 5 min threshold
            activity.duration = (activity.duration * 0.7 + duration * 0.3)
            
        # Save updates
        self._save_database()
        
    def _load_database(self):
        """Load research database from file."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                self.sources = {url: ResearchSource(**source_data)
                              for url, source_data in data['sources'].items()}
                self.activities = {name: Activity(**activity_data)
                                 for name, activity_data in data['activities'].items()}
                self.keywords = set(data['keywords'])
        except FileNotFoundError:
            logging.info("No existing database found. Creating new database.")
            self._initialize_default_activities()
            
    def _save_database(self):
        """Save research database to file."""
        data = {
            'sources': {url: source.__dict__ for url, source in self.sources.items()},
            'activities': {name: activity.__dict__ 
                         for name, activity in self.activities.items()},
            'keywords': list(self.keywords)
        }
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
            
    def _initialize_default_activities(self):
        """Initialize default activity database."""
        self.activities = {
            'meditation': Activity(
                name='meditation',
                duration=timedelta(minutes=20),
                intensity=0.2,
                category='meditation',
                recovery_impact=0.8,
                neuroplasticity_boost=0.9,
                eeg_compatibility=0.9,
                recommended_time='morning',
                contraindications=['high_fatigue']
            ),
            'light_exercise': Activity(
                name='light_exercise',
                duration=timedelta(minutes=30),
                intensity=0.5,
                category='exercise',
                recovery_impact=0.6,
                neuroplasticity_boost=0.7,
                eeg_compatibility=0.7,
                recommended_time='afternoon',
                contraindications=['low_recovery']
            ),
            'reading': Activity(
                name='reading',
                duration=timedelta(minutes=45),
                intensity=0.3,
                category='learning',
                recovery_impact=0.5,
                neuroplasticity_boost=0.8,
                eeg_compatibility=0.8,
                recommended_time='evening',
                contraindications=['high_cognitive_load']
            )
        }
