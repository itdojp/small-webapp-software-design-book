export type UsecaseError =
  | { code: "forbidden"; message: string }
  | { code: "not_found"; message: string }
  | { code: "conflict"; message: string }
  | { code: "invalid"; message: string };
