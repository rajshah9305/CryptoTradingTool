import jwt from 'jsonwebtoken';
import { argon2id } from 'hash-wasm';
import { randomBytes } from 'crypto';
import { User } from '../types';

export class SecurityService {
    private readonly JWT_SECRET: string;
    private readonly JWT_EXPIRY: string = '1h';
    private readonly REFRESH_TOKEN_EXPIRY: string = '7d';

    constructor() {
        this.JWT_SECRET = process.env.JWT_SECRET!;
        if (!this.JWT_SECRET) {
            throw new Error('JWT_SECRET is not set');
        }
    }

    async hashPassword(password: string): Promise<string> {
        const salt = randomBytes(16);
        return await argon2id({
            password,
            salt,
            timeCost: 2,
            memoryCost: 65536,
            parallelism: 1,
            outputLen: 32,
        });
    }

    async verifyPassword(hash: string, password: string): Promise<boolean> {
        try {
            const isValid = await argon2id.verify(hash, password);
            return isValid;
        } catch {
            return false;
        }
    }

    generateTokens(user: User): { accessToken: string; refreshToken: string } {
        const accessToken = jwt.sign(
            { userId: user.id, roles: user.roles },
            this.JWT_SECRET,
            { expiresIn: this.JWT_EXPIRY }
        );

        const refreshToken = jwt.sign(
            { userId: user.id, tokenVersion: user.tokenVersion },
            this.JWT_SECRET,
            { expiresIn: this.REFRESH_TOKEN_EXPIRY }
        );

        return { accessToken, refreshToken };
    }

    validateToken(token: string): any {
        try {
            return jwt.verify(token, this.JWT_SECRET);
        } catch {
            return null;
        }
    }

    refreshAccessToken(refreshToken: string): string | null {
        try {
            const payload = jwt.verify(refreshToken, this.JWT_SECRET);
            return jwt.sign(
                { userId: payload.userId, roles: payload.roles },
                this.JWT_SECRET,
                { expiresIn: this.JWT_EXPIRY }
            );
        } catch {
            return null;
        }
    }
}