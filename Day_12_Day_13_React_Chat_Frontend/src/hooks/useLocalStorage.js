import { useEffect, useState } from "react";

export function useLocalStorage(key, initialValue) {
    const [value, setValue] = useState(() => {
        try {
            const stored = localStorage.getItem(key);

            if (stored !== null) {
                return JSON.parse(stored);
            }

            return typeof initialValue === "function"
                ? initialValue()
                : initialValue;
        } catch (error) {
            console.error("Could not read localStorage:", error);

            return typeof initialValue === "function"
                ? initialValue()
                : initialValue;
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem(
                key,
                JSON.stringify(value)
            );
        } catch (error) {
            console.error("Could not save to localStorage:", error);
        }
    }, [key, value]);

    return [value, setValue];
}