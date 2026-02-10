import { useEffect, useState, useRef } from 'react';
import type { LogEvent, ImplementationPlan } from '../lib/types';

export function useLogStream() {
    const [logs, setLogs] = useState<LogEvent[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [plan, setPlan] = useState<ImplementationPlan | null>(null);

    const eventSourceRef = useRef<EventSource | null>(null);

    useEffect(() => {
        // In production, use relative path if served from same origin
        const url = "http://localhost:8000/stream/logs";

        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            console.log("Connected to log stream");
            setIsConnected(true);
        };

        eventSource.onmessage = (event) => {
            try {
                const data: LogEvent = JSON.parse(event.data);
                setLogs((prev) => [...prev, data]);

                // If it's a plan event, update the plan state
                if (data.type === "plan" || (data.type === "done" && data.content.plan)) {
                    // Handle plan updates
                    if (data.type === "done") {
                        setPlan(data.content.plan);
                    } else {
                        setPlan(data.content); // If direct plan event
                    }
                }
            } catch (e) {
                console.error("Error parsing event", e);
            }
        };

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            // Optional: reconnect logic
            setIsConnected(false);
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, []);

    const clearLogs = () => setLogs([]);

    return { logs, isConnected, plan, clearLogs };
}
