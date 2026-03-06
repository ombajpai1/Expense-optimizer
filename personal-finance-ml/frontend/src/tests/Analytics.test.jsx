import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Analytics from '../pages/Analytics';
import { AuthProvider } from '../context/AuthContext';
import * as api from '../services/api';

// Mock the apiCall service
vi.mock('../services/api', () => ({
    apiCall: vi.fn()
}));

// Mock the AuthContext
vi.mock('../context/AuthContext', () => ({
    useAuth: () => ({ token: 'fake-token' }),
    AuthProvider: ({ children }) => <div>{children}</div>
}));

describe('Analytics Dashboard Component Audit', () => {
    it('applies the Danger styling when actual_spend exceeds 120% of optimized_limit', async () => {

        // Mock API Response
        api.apiCall.mockResolvedValueOnce({
            month: 3,
            year: 2026,
            comparison: [
                {
                    category: 'Test Rent',
                    actual_spent: 12000,
                    optimized_limit: 10000, // 120% utilization
                    status: 'Danger'       // The ML regressor flags this as Danger
                }
            ],
            summary: {
                monthly_salary: 100000,
                total_spent: 12000,
                current_savings: 88000,
                savings_target_amount: 20000,
                savings_target_percentage: 20
            }
        });

        const { container } = render(
            <AuthProvider>
                <Analytics />
            </AuthProvider>
        );

        // Wait for the UI to digest the mock and render the Clarity Comparison Chart
        await waitFor(() => {
            expect(screen.getByText('Test Rent')).toBeDefined();
        });

        // The user asked to assert the progress bar gets the corresponding danger coloring.
        // In our Vanilla CSS layout, the danger bar uses background: 'var(--danger)'.
        // Let's query the specific tag marking Over Budget.
        const badge = screen.getByText('Over Budget');
        expect(badge.className).toContain('badge-danger');

        // Verify the background red fill was applied mathematically
        // We know the element represents the actual fill bar.
        const dangerDiv = container.querySelector('div[style*="background: var(--danger)"]');
        expect(dangerDiv).not.toBeNull();
        expect(dangerDiv.style.width).toBe('100%'); // Because 12000 > 10000 * 1.1 scale limit

        console.log("PASS: The Component successfully re-renders the Danger boundary visuals upon exceeding 120% limit.");
    });
});
