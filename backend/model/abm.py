"""Agent-Based Model for communication campaign simulation."""

import numpy as np
import networkx as nx
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from typing import Dict, List, Optional, Any
from enum import IntEnum

from ..schemas import KPICategory, MediaMix, WordOfMouthConfig


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
        
        # Agent attributes with random initialization
        self.interest_level = np.random.beta(2, 5)  # Skewed toward lower interest
        self.receptivity = np.random.beta(2, 3)     # Moderate receptivity
        self.influence = np.random.exponential(0.5)  # Long tail distribution
        
        # State variables
        self.state = CustomerState.UNAWARE
        self.days_in_state = 0
        self.last_exposure = -999  # Days since last media exposure
        
        # Memory of interactions
        self.media_exposures = 0
        self.wom_received = 0
        
    def step(self) -> None:
        """Agent step - process media exposure and word-of-mouth."""
        self.days_in_state += 1
        
        # Media exposure effect
        self._process_media_exposure()
        
        # Word-of-mouth effect
        self._process_word_of_mouth()
        
        # Forgetting/decay effect
        self._process_forgetting()
        
        # State transition logic
        self._update_state()
    
    def _process_media_exposure(self) -> None:
        """Process media exposure based on media mix."""
        media_mix = self.model.media_mix
        
        for channel, config in [
            ("sns", media_mix.sns),
            ("video", media_mix.video), 
            ("search", media_mix.search)
        ]:
            # Probability of exposure based on budget share and reach
            exposure_prob = config.share * 0.1  # Base exposure probability
            
            if np.random.random() < exposure_prob:
                self.media_exposures += 1
                self.last_exposure = 0
                
                # Effect probability based on alpha and receptivity
                effect_prob = config.alpha * self.receptivity
                
                if np.random.random() < effect_prob:
                    self._advance_state()
    
    def _process_word_of_mouth(self) -> None:
        """Process word-of-mouth from network neighbors."""
        neighbors = list(self.model.network.neighbors(self.unique_id))
        
        for neighbor_id in neighbors:
            neighbor = self.model.agents_dict.get(neighbor_id)
            if neighbor is None:
                continue
            
            # High-state agents generate WoM
            if neighbor.state >= CustomerState.LIKING:
                wom_prob = self.model.wom_config.p_generate * neighbor.influence * 0.1
                
                if np.random.random() < wom_prob:
                    self.wom_received += 1
                    
                    # WoM effect based on trust and receptivity
                    effect_prob = 0.05 * self.receptivity  # WoM is more effective than media
                    
                    if np.random.random() < effect_prob:
                        self._advance_state()
    
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
        for _ in range(self.steps):
            self.step()
        
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