import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(
  request: NextRequest,
  { params }: { params: { sessionKey: string; userId: string } }
) {
  try {
    const { sessionKey, userId } = params;
    
    const response = await fetch(`${BACKEND_URL}/api/v1/user-sessions/${sessionKey}/set-user/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const session = await response.json();
    return NextResponse.json(session);
  } catch (error) {
    console.error('Error setting current user:', error);
    return NextResponse.json(
      { error: 'Failed to set current user' },
      { status: 500 }
    );
  }
}
