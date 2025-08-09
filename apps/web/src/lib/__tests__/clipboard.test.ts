import { copyText } from '../clipboard';

describe('copyText', () => {
  it('uses navigator.clipboard when available', async () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    await copyText('hello');
    expect(writeText).toHaveBeenCalledWith('hello');
  });

  it('falls back to execCommand when clipboard API missing', async () => {
    // @ts-ignore
    navigator.clipboard = undefined;
    (document as any).execCommand = () => true;
    const execSpy = jest.spyOn(document, 'execCommand');
    const appendChild = jest.spyOn(document.body, 'appendChild');
    const removeChild = jest.spyOn(document.body, 'removeChild');
    await copyText('hi');
    expect(execSpy).toHaveBeenCalledWith('copy');
    expect(appendChild).toHaveBeenCalled();
    expect(removeChild).toHaveBeenCalled();
    execSpy.mockRestore();
    appendChild.mockRestore();
    removeChild.mockRestore();
  });
});
