// Copies provided text to the user's clipboard. Falls back to the legacy
// `document.execCommand('copy')` API when the modern clipboard API is
// unavailable.
export async function copyText(text: string): Promise<void> {
  if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.top = '0';
  textarea.style.left = '0';
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  const successful = document.execCommand('copy');
  document.body.removeChild(textarea);
  if (!successful) {
    throw new Error('Copy command was unsuccessful');
  }
}
