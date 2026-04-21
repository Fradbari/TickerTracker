import { render, screen, fireEvent } from '@testing-library/react'
import { AdminSettings } from '../../src/features/admin/components/AdminSettings'
import { describe, it, expect, vi } from 'vitest'

// Mock fetch API globalmente
global.fetch = vi.fn()

describe('AdminSettings Component', () => {
  it('mostra i pulsanti di backup e ripristino di GDrive', () => {
    // Setup di base
    render(<AdminSettings />)
    
    expect(screen.getByText('Backup su GDrive')).toBeInTheDocument()
    expect(screen.getByText('Ripristina da GDrive')).toBeInTheDocument()
  })

  it('apre il modale di conferma per il ripristino ed emette il comando', async () => {
    render(<AdminSettings />)
    
    const restoreBtn = screen.getByText('Ripristina da GDrive')
    fireEvent.click(restoreBtn)
    
    expect(screen.getByText('Conferma Ripristino')).toBeInTheDocument()
    
    const confirmBtn = screen.getByText('Conferma')
    fireEvent.click(confirmBtn)
    
    expect(global.fetch).toHaveBeenCalledWith('/api/sync/import', expect.objectContaining({
      method: 'POST'
    }))
  })
})
