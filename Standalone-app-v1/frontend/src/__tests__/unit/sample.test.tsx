import { renderWithProviders, screen, userEvent } from '../utils/renderWithProviders';
import { describe, it, expect } from 'vitest';
import React from 'react';

const TestComponent = () => {
    return <div>Hello World</div>;
};

describe('Sample Test', () => {
    it('should render successfully', () => {
        renderWithProviders(<TestComponent />);
        expect(screen.getByText('Hello World')).toBeInTheDocument();
    });
});
