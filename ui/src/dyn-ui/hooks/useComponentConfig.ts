import { useState, useEffect, useCallback } from 'react';

// Default backend URL - in a real app this would be an env var
const API_BASE_URL = 'http://localhost:3001/api';

export interface ComponentConfigResult<T> {
    config: T | null;
    loading: boolean;
    error: Error | null;
    refresh: () => void;
}

/**
 * Hook to fetch component configuration from the backend
 * @param componentId The ID of the component to fetch
 * @param defaultConfig Optional default configuration to use while loading or on error
 */
export function useComponentConfig<T>(
    componentId: number | string | undefined,
    defaultConfig?: T
): ComponentConfigResult<T> {
    const [config, setConfig] = useState<T | null>(defaultConfig || null);
    const [loading, setLoading] = useState<boolean>(!!componentId);
    const [error, setError] = useState<Error | null>(null);

    const fetchConfig = useCallback(async () => {
        if (!componentId) {
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE_URL}/components/${componentId}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch config: ${response.statusText}`);
            }

            const data = await response.json();

            // The backend returns the component object with a 'configuration' property
            if (data && data.configuration) {
                setConfig({
                    ...defaultConfig,
                    ...data.configuration,
                    // Preserve essential metadata for rendering
                    id: data.id,
                    componentType: data.componentType,
                    name: data.name
                });
            } else {
                // Fallback if structure is different
                setConfig({
                    ...defaultConfig,
                    ...data
                });
            }
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Unknown error'));
            console.error('Error fetching component config:', err);
        } finally {
            setLoading(false);
        }
    }, [componentId, defaultConfig]);

    useEffect(() => {
        fetchConfig();
    }, [fetchConfig]);

    return { config, loading, error, refresh: fetchConfig };
}
