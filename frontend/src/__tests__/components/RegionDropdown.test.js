import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import RegionDropdown from '../../components/RegionDropdown/RegionDropdown';
import { listRegions } from '../../services/regions';

jest.mock('../../services/regions');
jest.mock('react-widgets/Multiselect', () => ({ data, value, onChange }) => (
  <div>
    <p>Regions: {data.map((region) => region.name).join(', ')}</p>
    <button type="button" onClick={() => onChange([])}>Clear</button>
    <span data-testid="value-count">{value.length}</span>
  </div>
));

describe('RegionDropdown', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches and displays regions', async () => {
    listRegions.mockResolvedValue([
      { id: 1, name: 'Europe' },
      { id: 2, name: 'Asia' }
    ]);

    render(<RegionDropdown value={[]} onChange={jest.fn()} />);

    await waitFor(() => expect(listRegions).toHaveBeenCalled());
    expect(await screen.findByText(/regions: europe, asia/i)).toBeInTheDocument();
  });
});
