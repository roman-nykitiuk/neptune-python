export const loadState = key => {
  const serializedState = localStorage.getItem(key);
  return JSON.parse(serializedState) || { requesting: false };
};

export const saveState = (key, state) => {
  const serializedState = JSON.stringify(state);
  localStorage.setItem(key, serializedState);
};

export const removeState = key => {
  localStorage.removeItem(key);
};
