import { Note } from './note.entity';
import { Flowchart } from './flowchart.entity';
export declare class User {
    id: number;
    email: string;
    name: string;
    password: string;
    notes: Note[];
    flowcharts: Flowchart[];
}
