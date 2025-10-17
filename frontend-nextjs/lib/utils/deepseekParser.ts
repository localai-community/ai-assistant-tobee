/**
 * DeepSeek reasoning format parser
 * Parses responses with <think>...</think> tags to separate thinking and answer content
 */

export interface DeepSeekParsed {
  thinking: string;
  answer: string;
  isDeepSeekFormat: boolean;
}

/**
 * Parse DeepSeek reasoning format with <think>...</think> tags.
 * Also handles cases where only </think> tag is present (missing opening tag).
 * 
 * @param responseText - The full response text from DeepSeek
 * @returns Object containing thinking, answer, and isDeepSeekFormat keys
 */
export function parseDeepSeekReasoning(responseText: string): DeepSeekParsed {
  // Check if response contains DeepSeek reasoning format with both tags
  const thinkPattern = /<think>([\s\S]*?)<\/think>/;
  const matches = responseText.match(thinkPattern);
  
  if (matches) {
    // Extract thinking content
    const thinkingContent = matches[1].trim();
    
    // Extract answer content (everything after </think>)
    const answerPattern = /<\/think>([\s\S]*)/;
    const answerMatch = responseText.match(answerPattern);
    const answerContent = answerMatch ? answerMatch[1].trim() : "";
    
    return {
      thinking: thinkingContent,
      answer: answerContent,
      isDeepSeekFormat: true
    };
  } else {
    // Check if there's only a closing </think> tag (missing opening tag)
    const thinkEndIndex = responseText.indexOf('</think>');
    if (thinkEndIndex !== -1) {
      // Extract thinking content (everything before </think>)
      const thinkingContent = responseText.substring(0, thinkEndIndex).trim();
      
      // Extract answer content (everything after </think>)
      const answerContent = responseText.substring(thinkEndIndex + 8).trim();
      
      return {
        thinking: thinkingContent,
        answer: answerContent,
        isDeepSeekFormat: true
      };
    }
    
    // Not DeepSeek format, return as regular response
    return {
      thinking: "",
      answer: responseText,
      isDeepSeekFormat: false
    };
  }
}

/**
 * Check if a response contains DeepSeek reasoning format
 * @param responseText - The response text to check
 * @returns true if the response contains <think> tags or </think> tag
 */
export function isDeepSeekFormat(responseText: string): boolean {
  return /<think>/.test(responseText) || /<\/think>/.test(responseText);
}

/**
 * Extract thinking content from a partial response (for streaming)
 * @param responseText - The partial response text
 * @returns The thinking content if available, empty string otherwise
 */
export function extractThinkingContent(responseText: string): string {
  const thinkStart = responseText.indexOf('<think>');
  if (thinkStart === -1) return '';
  
  const thinkEnd = responseText.indexOf('</think>');
  if (thinkEnd === -1) {
    // Still in thinking phase, return content after <think>
    return responseText.substring(thinkStart + 7).trim();
  } else {
    // Complete thinking section
    return responseText.substring(thinkStart + 7, thinkEnd).trim();
  }
}

/**
 * Extract answer content from a partial response (for streaming)
 * @param responseText - The partial response text
 * @returns The answer content if available, empty string otherwise
 */
export function extractAnswerContent(responseText: string): string {
  const thinkEnd = responseText.indexOf('</think>');
  if (thinkEnd === -1) return '';
  
  // Return content after </think>
  return responseText.substring(thinkEnd + 8).trim();
}
