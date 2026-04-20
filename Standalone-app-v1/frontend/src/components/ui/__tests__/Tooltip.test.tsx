import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Tooltip } from '../Tooltip';

describe('Tooltip component', () => {
    it('renders children correctly', () => {
        render(<Tooltip content="Test Tooltip"><span>Hover Me</span></Tooltip>);
        expect(screen.getByText('Hover Me')).toBeTruthy();
    });

    it('shows tooltip on mouse enter and hides on mouse leave', () => {
        render(<Tooltip content="Tooltip Content"><span>Hover Me</span></Tooltip>);
        const child = screen.getByText('Hover Me');
        
        fireEvent.mouseEnter(child);
        expect(screen.getByText('Tooltip Content')).toBeTruthy();
        
        fireEvent.mouseLeave(child);
        expect(screen.queryByText('Tooltip Content')).toBeNull();
    });
});