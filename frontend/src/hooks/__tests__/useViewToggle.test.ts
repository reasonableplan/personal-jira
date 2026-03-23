import { renderHook, act } from "@testing-library/react";
import { useViewToggle } from "../useViewToggle";
import { VIEW_TYPES, VIEW_STORAGE_KEY, DEFAULT_VIEW } from "../../types/view";

const mockStorage: Record<string, string> = {};

beforeEach(() => {
  Object.keys(mockStorage).forEach((key) => delete mockStorage[key]);
  jest.spyOn(Storage.prototype, "getItem").mockImplementation(
    (key: string) => mockStorage[key] ?? null
  );
  jest.spyOn(Storage.prototype, "setItem").mockImplementation(
    (key: string, value: string) => {
      mockStorage[key] = value;
    }
  );
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe("useViewToggle", () => {
  it("returns default view when no stored value", () => {
    const { result } = renderHook(() => useViewToggle());
    expect(result.current.view).toBe(DEFAULT_VIEW);
  });

  it("reads stored view from localStorage", () => {
    mockStorage[VIEW_STORAGE_KEY] = VIEW_TYPES.TABLE;
    const { result } = renderHook(() => useViewToggle());
    expect(result.current.view).toBe(VIEW_TYPES.TABLE);
  });

  it("falls back to default for invalid stored value", () => {
    mockStorage[VIEW_STORAGE_KEY] = "invalid";
    const { result } = renderHook(() => useViewToggle());
    expect(result.current.view).toBe(DEFAULT_VIEW);
  });

  it("toggles from board to table", () => {
    const { result } = renderHook(() => useViewToggle());
    act(() => result.current.toggle());
    expect(result.current.view).toBe(VIEW_TYPES.TABLE);
  });

  it("toggles from table to board", () => {
    mockStorage[VIEW_STORAGE_KEY] = VIEW_TYPES.TABLE;
    const { result } = renderHook(() => useViewToggle());
    act(() => result.current.toggle());
    expect(result.current.view).toBe(VIEW_TYPES.BOARD);
  });

  it("persists view change to localStorage", () => {
    const { result } = renderHook(() => useViewToggle());
    act(() => result.current.toggle());
    expect(localStorage.setItem).toHaveBeenCalledWith(
      VIEW_STORAGE_KEY,
      VIEW_TYPES.TABLE
    );
  });

  it("sets specific view with setView", () => {
    const { result } = renderHook(() => useViewToggle());
    act(() => result.current.setView(VIEW_TYPES.TABLE));
    expect(result.current.view).toBe(VIEW_TYPES.TABLE);
    expect(localStorage.setItem).toHaveBeenCalledWith(
      VIEW_STORAGE_KEY,
      VIEW_TYPES.TABLE
    );
  });

  it("isBoard and isTable reflect current view", () => {
    const { result } = renderHook(() => useViewToggle());
    expect(result.current.isBoard).toBe(true);
    expect(result.current.isTable).toBe(false);
    act(() => result.current.toggle());
    expect(result.current.isBoard).toBe(false);
    expect(result.current.isTable).toBe(true);
  });
});
