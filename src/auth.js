import jwt from 'jsonwebtoken';

const secret = () => process.env.JWT_SECRET || 'dev-only-secret-change-me';

export function signToken(admin) {
  return jwt.sign({ sub: admin.id, username: admin.username, role: admin.role }, secret(), { expiresIn: '8h' });
}

export function requireAuth(req,res,next) {
  const header=req.headers.authorization || '';
  const token=header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return res.status(401).json({success:false,message:'Authentication required'});
  try { req.user=jwt.verify(token, secret()); next(); }
  catch { return res.status(401).json({success:false,message:'Invalid or expired token'}); }
}
