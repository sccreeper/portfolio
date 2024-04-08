/**
 * 
 * @param {number} val 
 * @param {number} min 
 * @param {number} max 
 * @returns 
 */
export function clamp(val, min, max) {
    
    if (val <= min) {
        return min
    } else if (val >= max) {
        return max
    } else {
        return val
    }

}