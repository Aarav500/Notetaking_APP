import { useState, useEffect, createContext, useContext } from "react";

const TOAST_REMOVE_DELAY = 1000;

const ToastActionType = {
  ADD_TOAST: "ADD_TOAST",
  UPDATE_TOAST: "UPDATE_TOAST",
  DISMISS_TOAST: "DISMISS_TOAST",
  REMOVE_TOAST: "REMOVE_TOAST",
};

let count = 0;

function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER;
  return count.toString();
}

const ToastContext = createContext({
  toasts: [],
  toast: () => {},
  dismiss: () => {},
  update: () => {},
});

function reducer(state, action) {
  switch (action.type) {
    case ToastActionType.ADD_TOAST:
      return {
        ...state,
        toasts: [...state.toasts, { ...action.toast, id: action.toast.id || genId() }],
      };
    case ToastActionType.UPDATE_TOAST:
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      };
    case ToastActionType.DISMISS_TOAST:
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toastId || (action.toastId === undefined && !t.open)
            ? { ...t, open: false }
            : t
        ),
      };
    case ToastActionType.REMOVE_TOAST:
      if (action.toastId === undefined) {
        return {
          ...state,
          toasts: [],
        };
      }
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      };
  }
}

export function ToastProvider({ children }) {
  const [state, setState] = useState({ toasts: [] });

  const dispatch = (action) => {
    setState((prevState) => reducer(prevState, action));
  };

  const toast = (props) => {
    const id = genId();
    const newToast = {
      id,
      open: true,
      variant: "default",
      ...props,
    };

    dispatch({ type: ToastActionType.ADD_TOAST, toast: newToast });

    return id;
  };

  const update = (id, props) => {
    dispatch({
      type: ToastActionType.UPDATE_TOAST,
      toast: { ...props, id },
    });
  };

  const dismiss = (id) => {
    dispatch({ type: ToastActionType.DISMISS_TOAST, toastId: id });
  };

  useEffect(() => {
    const timeouts = [];

    state.toasts.forEach((toast) => {
      if (!toast.open && !toast.removing) {
        const timeout = setTimeout(() => {
          dispatch({
            type: ToastActionType.REMOVE_TOAST,
            toastId: toast.id,
          });
        }, TOAST_REMOVE_DELAY);

        timeouts.push(timeout);

        dispatch({
          type: ToastActionType.UPDATE_TOAST,
          toast: { ...toast, removing: true },
        });
      }
    });

    return () => {
      timeouts.forEach((timeout) => clearTimeout(timeout));
    };
  }, [state.toasts]);

  return (
    <ToastContext.Provider
      value={{
        toasts: state.toasts,
        toast,
        dismiss,
        update,
      }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);

  if (context === undefined) {
    throw new Error("useToast must be used within a ToastProvider");
  }

  return context;
}