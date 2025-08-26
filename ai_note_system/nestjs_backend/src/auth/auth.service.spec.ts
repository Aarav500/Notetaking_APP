import { Test, TestingModule } from '@nestjs/testing';
import { AuthService } from './auth.service';
import { UsersService } from '../users/users.service';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import * as bcrypt from 'bcrypt';

describe('AuthService', () => {
  let service: AuthService;
  const usersServiceMock = {
    create: jest.fn(),
    findByEmail: jest.fn(),
    findById: jest.fn(),
    updatePassword: jest.fn(),
  };

  const jwtServiceMock = {
    signAsync: jest.fn().mockResolvedValue('jwt_token'),
  } as unknown as JwtService;

  const configServiceMock = {
    get: jest.fn((key: string, defaultValue?: any) => {
      if (key === 'RESET_TOKEN_TTL_MS') return 60000;
      if (key === 'JWT_SECRET') return 'dev_secret';
      if (key === 'JWT_EXPIRES_IN') return '1d';
      return defaultValue;
    }),
  } as unknown as ConfigService;

  beforeEach(async () => {
    jest.clearAllMocks();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        { provide: UsersService, useValue: usersServiceMock },
        { provide: JwtService, useValue: jwtServiceMock },
        { provide: ConfigService, useValue: configServiceMock },
      ],
    }).compile();

    service = module.get<AuthService>(AuthService);
  });

  it('should register and return token', async () => {
    usersServiceMock.create.mockResolvedValue({ id: 1, email: 'a@b.com', name: 'A', password: 'x' });
    const res = await service.register('a@b.com', 'secret123', 'A');
    expect(res.token).toBe('jwt_token');
    expect(res.user).toEqual({ id: 1, email: 'a@b.com', name: 'A' });
    expect(usersServiceMock.create).toHaveBeenCalledWith('a@b.com', 'secret123', 'A');
  });

  it('should login with valid credentials', async () => {
    const hash = await bcrypt.hash('secret123', 10);
    usersServiceMock.findByEmail.mockResolvedValue({ id: 2, email: 'b@b.com', name: 'B', password: hash });
    const res = await service.login('b@b.com', 'secret123');
    expect(res.token).toBe('jwt_token');
    expect(res.user).toEqual({ id: 2, email: 'b@b.com', name: 'B' });
  });

  it('should issue reset token and reset password', async () => {
    usersServiceMock.findByEmail.mockResolvedValue({ id: 3, email: 'c@c.com', name: 'C', password: 'x' });
    const { token } = await service.forgotPassword('c@c.com');
    expect(token).toBeDefined();

    await service.resetPassword(token, 'newsecret');
    expect(usersServiceMock.updatePassword).toHaveBeenCalledWith(3, 'newsecret');
  });

  it('should return masked message for unknown email in forgotPassword', async () => {
    usersServiceMock.findByEmail.mockResolvedValue(null);
    const res = await service.forgotPassword('unknown@example.com');
    expect(res.message).toBe('If the email exists, a reset link has been sent.');
  });

  it('should return user profile on me()', async () => {
    usersServiceMock.findById.mockResolvedValue({ id: 4, email: 'd@d.com', name: 'D', password: 'x' });
    const res = await service.me(4);
    expect(res.user).toEqual({ id: 4, email: 'd@d.com', name: 'D' });
  });
});
