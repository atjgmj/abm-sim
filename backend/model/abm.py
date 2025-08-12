"""Agent-Based Model for communication campaign simulation."""

import numpy as np
import networkx as nx
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from typing import Dict, List, Optional, Any
from enum import IntEnum

from ..schemas import (
    KPICategory, MediaMix, WordOfMouthConfig, PersonalityConfig, 
    DemographicConfig, InfluencerConfig, PersonalityType
)


class CustomerState(IntEnum):
    """Customer funnel states."""
    UNAWARE = 0
    AWARE = 1
    INTERESTED = 2
    KNOWLEDGEABLE = 3
    LIKING = 4
    INTENT = 5
    ADOPTED = 6


STATE_TO_KPI = {
    CustomerState.AWARE: KPICategory.AWARENESS,
    CustomerState.INTERESTED: KPICategory.INTEREST,
    CustomerState.KNOWLEDGEABLE: KPICategory.KNOWLEDGE,
    CustomerState.LIKING: KPICategory.LIKING,
    CustomerState.INTENT: KPICategory.INTENT
}


class CustomerAgent(Agent):
    """Customer agent in the ABM simulation."""
    
    def __init__(self, unique_id: int, model: 'CommunicationModel'):
        super().__init__(model)
        self.unique_id = unique_id
        
        # Multi-dimensional personality traits
        self.personality = self._generate_personality()
        self.demographics = self._generate_demographics()
        self.is_influencer = self._determine_influencer_status()
        
        # Legacy attributes (now derived from personality/demographics)
        self.interest_level = self._calculate_interest_level()
        self.receptivity = self._calculate_receptivity()
        self.influence = self._calculate_influence()
        
        # State variables
        self.state = CustomerState.UNAWARE
        self.days_in_state = 0
        self.last_exposure = -999  # Days since last media exposure
        
        # Memory of interactions
        self.media_exposures = 0
        self.wom_received = 0
        
        # Time-varying attributes
        self.current_openness = self.personality['openness']
        self.current_receptivity = self.receptivity
    
    def _generate_personality(self) -> Dict[str, float]:
        """Generate personality traits based on Rogers' diffusion model."""
        # Sample personality type based on adoption curve
        rand = np.random.random()
        if rand < 0.025:
            p_type = PersonalityType.INNOVATOR
            openness = np.random.beta(8, 2)  # High openness
            social_influence = np.random.beta(2, 8)  # Low social influence need
            risk_tolerance = np.random.beta(7, 3)  # High risk tolerance
        elif rand < 0.16:  # 0.025 + 0.135
            p_type = PersonalityType.EARLY_ADOPTER
            openness = np.random.beta(6, 4)
            social_influence = np.random.beta(3, 7)
            risk_tolerance = np.random.beta(6, 4)
        elif rand < 0.5:   # 0.16 + 0.34
            p_type = PersonalityType.EARLY_MAJORITY
            openness = np.random.beta(4, 6)
            social_influence = np.random.beta(6, 4)
            risk_tolerance = np.random.beta(4, 6)
        elif rand < 0.84:  # 0.5 + 0.34
            p_type = PersonalityType.LATE_MAJORITY
            openness = np.random.beta(3, 7)
            social_influence = np.random.beta(7, 3)
            risk_tolerance = np.random.beta(3, 7)
        else:
            p_type = PersonalityType.LAGGARD
            openness = np.random.beta(2, 8)
            social_influence = np.random.beta(8, 2)
            risk_tolerance = np.random.beta(2, 8)
        
        media_affinity = np.random.beta(3, 3)  # Moderate baseline
        
        return {
            'type': p_type,
            'openness': openness,
            'social_influence': social_influence,
            'media_affinity': media_affinity,
            'risk_tolerance': risk_tolerance
        }
    
    def _generate_demographics(self) -> Dict[str, Any]:
        """Generate demographic attributes."""
        age_group = np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.20, 0.25, 0.25, 0.15])
        income_level = np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.20, 0.30, 0.25, 0.10])
        urban_rural = np.random.beta(6, 4)  # Skewed toward urban
        education_level = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.15, 0.35, 0.30, 0.15])
        
        return {
            'age_group': age_group,
            'income_level': income_level,
            'urban_rural': urban_rural,
            'education_level': education_level
        }
    
    def _determine_influencer_status(self) -> bool:
        """Determine if agent is an influencer based on personality."""
        if not self.model.influencer_config.enable_influencers:
            return False
        
        # Higher chance for early adopters and innovators
        base_prob = self.model.influencer_config.influencer_ratio
        if self.personality['type'] in [PersonalityType.INNOVATOR, PersonalityType.EARLY_ADOPTER]:
            prob = base_prob * 3.0
        else:
            prob = base_prob * 0.5
        
        return np.random.random() < prob
    
    def _calculate_interest_level(self) -> float:
        """Calculate interest level from personality and demographics."""
        base = self.personality['openness'] * 0.6 + self.personality['risk_tolerance'] * 0.4
        
        # Age factor (younger = more interested in new things)
        age_factor = (6 - self.demographics['age_group']) / 5.0 * 0.2
        
        # Education factor
        edu_factor = self.demographics['education_level'] / 5.0 * 0.1
        
        return np.clip(base + age_factor + edu_factor, 0, 1)
    
    def _calculate_receptivity(self) -> float:
        """Calculate media receptivity from personality and demographics."""
        base = self.personality['media_affinity'] * 0.7 + self.personality['openness'] * 0.3
        
        # Urban factor (urban = more media exposure)
        urban_factor = self.demographics['urban_rural'] * 0.1
        
        return np.clip(base + urban_factor, 0, 1)
    
    def _calculate_influence(self) -> float:
        """Calculate social influence from personality and demographics."""
        base = (self.personality['social_influence'] * 0.4 + 
                self.demographics['education_level'] / 5.0 * 0.3 +
                self.demographics['income_level'] / 5.0 * 0.3)
        
        # Influencer multiplier
        if self.is_influencer:
            base *= self.model.influencer_config.influence_multiplier
        
        return base
        
    def step(self) -> None:
        """Agent step - process media exposure and word-of-mouth."""
        self.days_in_state += 1
        
        # Update time-varying attributes
        self._update_time_varying_attributes()
        
        # Media exposure effect
        self._process_media_exposure()
        
        # Word-of-mouth effect
        self._process_word_of_mouth()
        
        # Forgetting/decay effect
        self._process_forgetting()
        
        # State transition logic
        self._update_state()
    
    def _update_time_varying_attributes(self) -> None:
        """Update attributes that change over time."""
        # Openness decreases slightly with repeated exposure (habituation)
        habituation_factor = 1 - (self.media_exposures * 0.001)  # Slow decrease
        self.current_openness = self.personality['openness'] * max(0.5, habituation_factor)
        
        # Receptivity varies based on recent exposure recency
        if self.last_exposure < 5:  # Recent exposure increases receptivity temporarily
            recency_boost = 0.1 * (5 - self.last_exposure) / 5
        else:
            recency_boost = 0
        
        self.current_receptivity = min(1.0, self.receptivity + recency_boost)
    
    def _process_media_exposure(self) -> None:
        """Process media exposure based on media mix and personal attributes."""
        media_mix = self.model.media_mix
        
        for channel, config in [
            ("sns", media_mix.sns),
            ("video", media_mix.video), 
            ("search", media_mix.search)
        ]:
            # Exposure probability adjusted by demographics and personality
            base_exposure_prob = config.share * 0.1
            
            # Channel-specific demographic adjustments
            demo_modifier = self._get_channel_demographic_modifier(channel)
            exposure_prob = base_exposure_prob * demo_modifier
            
            if np.random.random() < exposure_prob:
                self.media_exposures += 1
                self.last_exposure = 0
                
                # Effect probability using current (time-varying) receptivity
                effect_prob = config.alpha * self.current_receptivity * self.current_openness
                
                if np.random.random() < effect_prob:
                    self._advance_state()
                    
    def _get_channel_demographic_modifier(self, channel: str) -> float:
        """Get demographic modifier for specific media channel."""
        if channel == "sns":
            # Younger, urban, higher education more likely to use SNS
            age_factor = (6 - self.demographics['age_group']) / 5.0  # Younger = higher
            urban_factor = self.demographics['urban_rural']
            edu_factor = self.demographics['education_level'] / 5.0
            return 0.5 + (age_factor + urban_factor + edu_factor) * 0.3
        
        elif channel == "video":
            # More universal but still skews younger
            age_factor = (6 - self.demographics['age_group']) / 5.0 * 0.3
            income_factor = self.demographics['income_level'] / 5.0 * 0.2
            return 0.7 + age_factor + income_factor
        
        elif channel == "search":
            # Education and income driven
            edu_factor = self.demographics['education_level'] / 5.0 * 0.4
            income_factor = self.demographics['income_level'] / 5.0 * 0.3
            return 0.6 + edu_factor + income_factor
        
        return 1.0
    
    def _process_word_of_mouth(self) -> None:
        """Process word-of-mouth from network neighbors with enhanced modeling."""
        neighbors = list(self.model.network.neighbors(self.unique_id))
        
        for neighbor_id in neighbors:
            neighbor = self.model.agents_dict.get(neighbor_id)
            if neighbor is None:
                continue
            
            # High-state agents generate WoM
            if neighbor.state >= CustomerState.LIKING:
                # Enhanced WoM generation probability
                base_wom_prob = self.model.wom_config.p_generate * neighbor.influence * 0.1
                
                # Personality and demographic similarity bonus
                similarity_bonus = self._calculate_similarity_bonus(neighbor)
                wom_prob = base_wom_prob * (1 + similarity_bonus)
                
                if np.random.random() < wom_prob:
                    self.wom_received += 1
                    
                    # Enhanced WoM effect calculation
                    base_effect = 0.05 * self.current_receptivity
                    
                    # Social influence personality factor
                    social_factor = self.personality['social_influence']
                    
                    # Influencer effect
                    influencer_factor = 2.0 if neighbor.is_influencer else 1.0
                    
                    effect_prob = base_effect * social_factor * influencer_factor
                    
                    if np.random.random() < effect_prob:
                        self._advance_state()
    
    def _calculate_similarity_bonus(self, neighbor: 'CustomerAgent') -> float:
        """Calculate similarity bonus for WoM effectiveness."""
        # Age similarity
        age_diff = abs(self.demographics['age_group'] - neighbor.demographics['age_group'])
        age_similarity = max(0, 1 - age_diff / 4.0)  # Normalize to 0-1
        
        # Income similarity 
        income_diff = abs(self.demographics['income_level'] - neighbor.demographics['income_level'])
        income_similarity = max(0, 1 - income_diff / 4.0)
        
        # Urban-rural similarity
        urban_diff = abs(self.demographics['urban_rural'] - neighbor.demographics['urban_rural'])
        urban_similarity = max(0, 1 - urban_diff)
        
        # Weighted average similarity
        similarity = (age_similarity * 0.4 + income_similarity * 0.3 + urban_similarity * 0.3)
        
        return similarity * 0.3  # Max 30% bonus
    
    def _process_forgetting(self) -> None:
        """Process forgetting/decay over time."""
        # Forgetting probability increases with time since last exposure
        forget_prob = 0.01 * (1 + self.days_in_state * 0.1) * self.model.wom_config.decay
        
        if np.random.random() < forget_prob and self.state > CustomerState.UNAWARE:
            self.state = CustomerState(max(CustomerState.UNAWARE, self.state - 1))
            self.days_in_state = 0
    
    def _advance_state(self) -> None:
        """Advance agent to next state if possible."""
        if self.state < CustomerState.ADOPTED:
            self.state = CustomerState(self.state + 1)
            self.days_in_state = 0
    
    def _update_state(self) -> None:
        """Additional state transition logic based on time and characteristics."""
        # Natural progression probability based on interest level
        if self.state in [CustomerState.AWARE, CustomerState.INTERESTED]:
            progress_prob = self.interest_level * 0.02  # 2% base chance per day
            
            if np.random.random() < progress_prob:
                self._advance_state()


class CommunicationModel(Model):
    """ABM model for communication campaign simulation."""
    
    def __init__(
        self,
        network: nx.Graph,
        media_mix: MediaMix,
        wom_config: WordOfMouthConfig,
        personality_config: PersonalityConfig,
        demographic_config: DemographicConfig,
        influencer_config: InfluencerConfig,
        steps: int = 60,
        seed: Optional[int] = None
    ):
        # Initialize Model with seed parameter
        super().__init__(seed=seed)
        
        if seed is not None:
            np.random.seed(seed)
        
        self.network = network
        self.media_mix = media_mix
        self.wom_config = wom_config
        self.personality_config = personality_config
        self.demographic_config = demographic_config
        self.influencer_config = influencer_config
        self.steps = steps
        self.current_step = 0
        
        # Create scheduler
        self.schedule = RandomActivation(self)
        
        # Create agents dictionary for efficient lookup
        self.agents_dict = {}
        
        # Create agents for each network node
        for node_id in network.nodes():
            agent = CustomerAgent(node_id, self)
            self.schedule.add(agent)
            self.agents_dict[node_id] = agent
        
        # Data collection
        model_reporters = {"Day": "current_step"}
        for kpi in KPICategory:
            model_reporters[kpi.value] = self._make_kpi_collector(kpi)
        
        self.datacollector = DataCollector(model_reporters=model_reporters)
        
        # Collect initial data
        self.datacollector.collect(self)
    
    def _make_kpi_collector(self, kpi: KPICategory):
        """Create data collector function for specific KPI."""
        def collector(model) -> int:
            state = None
            for state_val, kpi_val in STATE_TO_KPI.items():
                if kpi_val == kpi:
                    state = state_val
                    break
            
            if state is None:
                return 0
                
            return sum(1 for agent in model.schedule.agents if agent.state >= state)
        
        return collector
    
    def step(self) -> None:
        """Model step - advance all agents."""
        self.current_step += 1
        self.schedule.step()
        self.datacollector.collect(self)
    
    def run(self) -> Dict[str, Any]:
        """Run the simulation for specified steps."""
        print(f"Starting simulation with {len(self.schedule.agents)} agents for {self.steps} steps")
        
        for step in range(self.steps):
            if step % 10 == 0:  # Log every 10 steps
                print(f"Simulation step {step}/{self.steps}")
            self.step()
        
        print("Simulation completed, collecting data...")
        
        # Extract data
        model_data = self.datacollector.get_model_vars_dataframe()
        
        # Convert to time series format
        series = []
        for _, row in model_data.iterrows():
            day = int(row['Day'])
            for kpi in KPICategory:
                series.append({
                    'day': day,
                    'metric': kpi,
                    'value': int(row[kpi.value])
                })
        
        # Calculate summary statistics
        summary = {}
        for kpi in KPICategory:
            values = model_data[kpi.value].values
            summary[kpi] = {
                'start': int(values[0]),
                'end': int(values[-1]),
                'delta': int(values[-1] - values[0])
            }
        
        return {
            'series': series,
            'summary': summary,
            'model_data': model_data
        }