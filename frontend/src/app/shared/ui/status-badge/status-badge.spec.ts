import { TestBed } from '@angular/core/testing';

import { StatusBadge } from './status-badge';

describe('StatusBadge', () => {
  it('shows the status as text and icon, not only as a colour', async () => {
    const fixture = TestBed.createComponent(StatusBadge);
    fixture.componentRef.setInput('status', 'FAILED');
    await fixture.whenStable();

    const badge = (fixture.nativeElement as HTMLElement).querySelector('.status-badge')!;
    expect(badge.textContent).toContain('FAILED');
    expect(badge.classList).toContain('status-badge--failed');
    expect(badge.querySelector('svg path')?.getAttribute('d')).toBeTruthy();
  });
});
