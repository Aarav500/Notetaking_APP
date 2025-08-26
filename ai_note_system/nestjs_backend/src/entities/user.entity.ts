import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from 'typeorm';
import { Note } from './note.entity';
import { Flowchart } from './flowchart.entity';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column({ nullable: true })
  name: string;

  @Column()
  password: string;

  @OneToMany(() => Note, note => note.user)
  notes: Note[];
  
  @OneToMany(() => Flowchart, flowchart => flowchart.user)
  flowcharts: Flowchart[];
}