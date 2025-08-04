/**
 * Decode HTML entities to their corresponding characters
 * Handles common entities like &#039; (') and &amp; (&)
 */
export function decodeHtmlEntities(text: string | null | undefined): string {
  if (!text) return '';
  
  // Create a temporary div element to decode HTML entities
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value;
}

/**
 * Decode HTML entities in user data fields
 */
export function decodeUserData(user: any) {
  return {
    ...user,
    first_name: decodeHtmlEntities(user.first_name),
    last_name: decodeHtmlEntities(user.last_name),
    department_name: decodeHtmlEntities(user.department_name),
    email: decodeHtmlEntities(user.email),
    username: decodeHtmlEntities(user.username),
  };
} 