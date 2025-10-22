import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { NotificationProvider, useNotification } from '../../contexts/NotificationContext';

jest.useFakeTimers();

const TestComponent = () => {
  const { showNotification, removeNotification, notifications } = useNotification();

  return (
    <div>
      <button
        type="button"
        onClick={() => showNotification('Hello World', 'success')}
      >
        Add Notification
      </button>
      {notifications.map((notification) => (
        <div key={notification.id}>
          <span>{notification.message}</span>
          <button type="button" onClick={() => removeNotification(notification.id)}>
            Dismiss
          </button>
        </div>
      ))}
    </div>
  );
};

describe('NotificationContext', () => {
  afterEach(() => {
    jest.clearAllTimers();
  });

  it('adds and removes notifications', () => {
    render(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );

    const trigger = screen.getByRole('button', { name: /add notification/i });

    act(() => {
      trigger.click();
    });

    expect(screen.getAllByText('Hello World').length).toBeGreaterThan(0);

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(screen.queryAllByText('Hello World')).toHaveLength(0);
  });

  it('allows manual dismissal', () => {
    render(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );

    const trigger = screen.getByRole('button', { name: /add notification/i });

    act(() => {
      trigger.click();
    });

    expect(screen.getAllByText('Hello World').length).toBeGreaterThan(0);

    act(() => {
      screen.getByRole('button', { name: /dismiss/i }).click();
    });

    expect(screen.queryAllByText('Hello World')).toHaveLength(0);
  });
});
