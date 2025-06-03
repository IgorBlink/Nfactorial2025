import { ChangeEvent, KeyboardEvent, FormEvent } from 'react';

export type InputChangeEvent = ChangeEvent<HTMLInputElement>;
export type TextareaChangeEvent = ChangeEvent<HTMLTextAreaElement>;
export type KeyboardEventType = KeyboardEvent<HTMLTextAreaElement>;
export type FormEventType = FormEvent<HTMLFormElement>; 