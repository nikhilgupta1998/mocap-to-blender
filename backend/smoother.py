"""
Smoothing filters for reducing jitter in pose tracking.
"""
import numpy as np
from typing import List, Dict, Optional
from scipy.signal import butter, filtfilt


class ExponentialMovingAverage:
    """Exponential Moving Average filter for real-time smoothing."""
    
    def __init__(self, alpha: float = 0.3):
        """
        Initialize EMA filter.
        
        Args:
            alpha: Smoothing factor (0-1). Lower = smoother but more lag.
        """
        self.alpha = alpha
        self.previous = None
    
    def smooth(self, landmarks: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Apply EMA smoothing to landmarks.
        
        Args:
            landmarks: List of landmark dictionaries with x, y, z coordinates
            
        Returns:
            Smoothed landmarks
        """
        if self.previous is None:
            self.previous = landmarks
            return landmarks
        
        smoothed = []
        for i, (current, prev) in enumerate(zip(landmarks, self.previous)):
            smoothed_lm = {
                'x': self.alpha * current['x'] + (1 - self.alpha) * prev['x'],
                'y': self.alpha * current['y'] + (1 - self.alpha) * prev['y'],
                'z': self.alpha * current['z'] + (1 - self.alpha) * prev['z'],
                'visibility': current.get('visibility', 1.0)
            }
            smoothed.append(smoothed_lm)
        
        self.previous = smoothed
        return smoothed
    
    def reset(self):
        """Reset the filter state."""
        self.previous = None


class KalmanFilter:
    """Kalman filter for sophisticated pose smoothing."""
    
    def __init__(
        self,
        process_noise: float = 0.01,
        measurement_noise: float = 0.1
    ):
        """
        Initialize Kalman filter.
        
        Args:
            process_noise: Process noise covariance
            measurement_noise: Measurement noise covariance
        """
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.states = None
        self.covariances = None
    
    def smooth(self, landmarks: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Apply Kalman filtering to landmarks.
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            Smoothed landmarks
        """
        if self.states is None:
            # Initialize states
            self.states = []
            self.covariances = []
            for lm in landmarks:
                self.states.append([lm['x'], lm['y'], lm['z']])
                self.covariances.append(np.eye(3))
            return landmarks
        
        smoothed = []
        for i, lm in enumerate(landmarks):
            # Prediction step
            predicted_state = self.states[i]
            predicted_cov = self.covariances[i] + np.eye(3) * self.process_noise
            
            # Update step
            measurement = np.array([lm['x'], lm['y'], lm['z']])
            innovation = measurement - predicted_state
            innovation_cov = predicted_cov + np.eye(3) * self.measurement_noise
            kalman_gain = predicted_cov @ np.linalg.inv(innovation_cov)
            
            # Update state and covariance
            updated_state = predicted_state + kalman_gain @ innovation
            updated_cov = (np.eye(3) - kalman_gain) @ predicted_cov
            
            self.states[i] = updated_state
            self.covariances[i] = updated_cov
            
            smoothed.append({
                'x': float(updated_state[0]),
                'y': float(updated_state[1]),
                'z': float(updated_state[2]),
                'visibility': lm.get('visibility', 1.0)
            })
        
        return smoothed
    
    def reset(self):
        """Reset the filter state."""
        self.states = None
        self.covariances = None


class OneEuroFilter:
    """One Euro filter for adaptive smoothing."""
    
    def __init__(
        self,
        min_cutoff: float = 1.0,
        beta: float = 0.007,
        d_cutoff: float = 1.0
    ):
        """
        Initialize One Euro filter.
        
        Args:
            min_cutoff: Minimum cutoff frequency
            beta: Cutoff slope
            d_cutoff: Derivative cutoff frequency
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.previous_values = None
        self.previous_derivatives = None
        self.previous_time = None
    
    def _smoothing_factor(self, t_e: float, cutoff: float) -> float:
        """Calculate smoothing factor."""
        r = 2 * np.pi * cutoff * t_e
        return r / (r + 1)
    
    def _exponential_smoothing(
        self,
        alpha: float,
        x: float,
        prev_x: float
    ) -> float:
        """Apply exponential smoothing."""
        return alpha * x + (1 - alpha) * prev_x
    
    def smooth(
        self,
        landmarks: List[Dict[str, float]],
        timestamp: float
    ) -> List[Dict[str, float]]:
        """
        Apply One Euro smoothing to landmarks.
        
        Args:
            landmarks: List of landmark dictionaries
            timestamp: Current timestamp in seconds
            
        Returns:
            Smoothed landmarks
        """
        if self.previous_values is None:
            self.previous_values = landmarks
            self.previous_derivatives = [{'x': 0, 'y': 0, 'z': 0} for _ in landmarks]
            self.previous_time = timestamp
            return landmarks
        
        t_e = timestamp - self.previous_time
        if t_e <= 0:
            t_e = 0.016  # ~60 FPS fallback
        
        smoothed = []
        for i, lm in enumerate(landmarks):
            prev_lm = self.previous_values[i]
            prev_deriv = self.previous_derivatives[i]
            
            # Smooth each coordinate
            smoothed_lm = {'visibility': lm.get('visibility', 1.0)}
            for coord in ['x', 'y', 'z']:
                # Derivative estimation
                deriv = (lm[coord] - prev_lm[coord]) / t_e
                alpha_d = self._smoothing_factor(t_e, self.d_cutoff)
                deriv_hat = self._exponential_smoothing(alpha_d, deriv, prev_deriv[coord])
                
                # Adaptive cutoff
                cutoff = self.min_cutoff + self.beta * abs(deriv_hat)
                alpha = self._smoothing_factor(t_e, cutoff)
                
                # Smooth value
                smoothed_lm[coord] = self._exponential_smoothing(alpha, lm[coord], prev_lm[coord])
                self.previous_derivatives[i][coord] = deriv_hat
            
            smoothed.append(smoothed_lm)
        
        self.previous_values = smoothed
        self.previous_time = timestamp
        return smoothed
    
    def reset(self):
        """Reset the filter state."""
        self.previous_values = None
        self.previous_derivatives = None
        self.previous_time = None
