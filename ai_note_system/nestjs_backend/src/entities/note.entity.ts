import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { User } from './user.entity';

@Entity('notes')
export class Note {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  // Use portable text type for cross-DB compatibility (SQLite/Postgres/Oracle)
  @Column({ type: 'text' })
  content: string;

  @Column({ default: false })
  is_ai_generated: boolean;

  @ManyToOne(() => User, user => user.notes)
  @JoinColumn({ name: 'user_id' })
  user: User;
}