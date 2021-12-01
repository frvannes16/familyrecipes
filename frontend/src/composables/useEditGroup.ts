
// Components register a callback to this map. The callback is called when an event is triggered.
const observerCallbacks = new Map<string, () => void>();

type EditableSuscriberOptions = {
    claimFocus: () => void
    relinquishFocus: () => void
    deregisterCallback: () => void
}


let focusedId: string | null = null;

export default () => {

    const genRandId = () => { 
        return Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5); 
    }

    const registerCallback = (callback: VoidFunction): EditableSuscriberOptions => {
        const id = genRandId();
        observerCallbacks.set(id, callback);

        const deregisterCallback = () => {
            if (observerCallbacks.has(id)) {
                observerCallbacks.delete(id);
            }
        };


        const claimFocus = () => {
            // Force the current focused component to close by calling its callback.
            if (focusedId) {
                const focusedCompCallback = observerCallbacks.get(focusedId);
                if (focusedCompCallback) {
                    focusedCompCallback();
                }
            }
            focusedId = id;
        };

        const relinquishFocus = () => {
            if (focusedId && focusedId == id) {
                focusedId = null;
            }
        };

        return {
            claimFocus,
            relinquishFocus,
            deregisterCallback
        };
    };

   

    return registerCallback;
}