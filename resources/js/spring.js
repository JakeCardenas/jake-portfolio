/**
 * Apple-style spring animations for vanilla JavaScript
 * Based on Apple's WWDC "Designing Fluid Interfaces" principles
 * 
 * Springs are interruptible, velocity-aware, and continuous.
 * They animate from the current presentation value, not the target.
 */

class Spring {
  constructor(config = {}) {
    // Apple's designer-friendly parameters
    this.damping = config.damping ?? 1.0; // 1.0 = critically damped (no overshoot)
    this.response = config.response ?? 0.4; // how quickly it reaches target (seconds)
    
    // Derived physics values (mass/stiffness/damping coefficient)
    this.mass = 1;
    this.stiffness = Math.pow(2 * Math.PI / this.response, 2);
    this.dampingCoeff = 4 * Math.PI * this.damping / this.response;
    
    // Animation state
    this.value = config.value ?? 0;
    this.target = config.target ?? 0;
    this.velocity = config.velocity ?? 0;
    this.isAnimating = false;
    this.rafId = null;
    this.lastTime = null;
    this.onUpdate = config.onUpdate ?? (() => {});
    this.onComplete = config.onComplete ?? (() => {});
    
    // Settling threshold
    this.epsilon = 0.001;
  }
  
  // Update target and optionally velocity (for gesture handoff)
  setTarget(newTarget, initialVelocity = null) {
    this.target = newTarget;
    if (initialVelocity !== null) {
      this.velocity = initialVelocity;
    }
    if (!this.isAnimating) {
      this.start();
    }
  }
  
  // Set current value (for interruptions)
  setValue(newValue) {
    this.value = newValue;
  }
  
  start() {
    if (this.isAnimating) return;
    this.isAnimating = true;
    this.lastTime = performance.now();
    this.tick();
  }
  
  stop() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.isAnimating = false;
    this.lastTime = null;
  }
  
  tick() {
    if (!this.isAnimating) return;
    
    const now = performance.now();
    const dt = this.lastTime ? Math.min((now - this.lastTime) / 1000, 0.064) : 0.016;
    this.lastTime = now;
    
    // Spring physics (semi-implicit Euler integration)
    const displacement = this.value - this.target;
    const springForce = -this.stiffness * displacement;
    const dampingForce = -this.dampingCoeff * this.velocity;
    const acceleration = (springForce + dampingForce) / this.mass;
    
    this.velocity += acceleration * dt;
    this.value += this.velocity * dt;
    
    // Check if settled
    const isSettled = 
      Math.abs(this.velocity) < this.epsilon && 
      Math.abs(displacement) < this.epsilon;
    
    if (isSettled) {
      this.value = this.target;
      this.velocity = 0;
      this.stop();
      this.onComplete(this.value);
    } else {
      this.onUpdate(this.value);
      this.rafId = requestAnimationFrame(() => this.tick());
    }
  }
  
  // Get current presentation value
  getCurrentValue() {
    return this.value;
  }
}

/**
 * Momentum projection using Apple's exponential decay model
 * Projects where an element will rest after a flick/throw
 */
function projectMomentum(velocity, decelerationRate = 0.998) {
  return (velocity / 1000) * decelerationRate / (1 - decelerationRate);
}

/**
 * Rubber-band resistance at boundaries
 * Returns damped displacement when overscrolling past edge
 */
function rubberBand(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}

/**
 * Velocity tracker for pointer/touch gestures
 * Maintains a short history to calculate release velocity
 */
class VelocityTracker {
  constructor(historySize = 5) {
    this.history = [];
    this.historySize = historySize;
  }
  
  add(position, timestamp) {
    this.history.push({ position, timestamp });
    if (this.history.length > this.historySize) {
      this.history.shift();
    }
  }
  
  getVelocity() {
    if (this.history.length < 2) return 0;
    
    const latest = this.history[this.history.length - 1];
    const earliest = this.history[0];
    const dt = (latest.timestamp - earliest.timestamp) / 1000;
    
    if (dt === 0) return 0;
    
    return (latest.position - earliest.position) / dt;
  }
  
  reset() {
    this.history = [];
  }
}

/**
 * Animate element with spring physics
 * High-level helper for common use cases
 */
function animateSpring(element, property, targetValue, config = {}) {
  // Read current presentation value from transform matrix
  const getCurrentTransformValue = (prop) => {
    const style = window.getComputedStyle(element);
    const matrix = new DOMMatrix(style.transform);
    
    switch(prop) {
      case 'x': return matrix.m41;
      case 'y': return matrix.m42;
      case 'scale': return matrix.a;
      default: return 0;
    }
  };
  
  const current = property.startsWith('transform') 
    ? getCurrentTransformValue(property.replace('transform-', ''))
    : parseFloat(getComputedStyle(element)[property]) || 0;
  
  const spring = new Spring({
    value: config.from ?? current,
    target: targetValue,
    velocity: config.velocity ?? 0,
    damping: config.damping ?? 1.0,
    response: config.response ?? 0.4,
    onUpdate: (value) => {
      if (property === 'transform-x') {
        element.style.transform = `translateX(${value}px)`;
      } else if (property === 'transform-y') {
        element.style.transform = `translateY(${value}px)`;
      } else if (property === 'transform-scale') {
        element.style.transform = `scale(${value})`;
      } else {
        element.style[property] = `${value}${config.unit || 'px'}`;
      }
    },
    onComplete: config.onComplete
  });
  
  spring.start();
  return spring;
}

export { Spring, projectMomentum, rubberBand, VelocityTracker, animateSpring };
