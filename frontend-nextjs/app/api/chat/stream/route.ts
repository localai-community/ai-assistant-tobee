import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward the request to the backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend responded with status: ${backendResponse.status}`);
    }

    // Check if the response is a stream
    const contentType = backendResponse.headers.get('content-type');
    if (!contentType || !contentType.includes('text/event-stream')) {
      throw new Error('Backend response is not a stream');
    }

    // Create a readable stream that forwards the backend response
    const stream = new ReadableStream({
      start(controller) {
        const reader = backendResponse.body?.getReader();
        
        if (!reader) {
          controller.close();
          return;
        }

        function pump(): Promise<void> {
          return reader!.read().then(({ done, value }) => {
            if (done) {
              controller.close();
              return;
            }
            
            // Forward the chunk to the client
            controller.enqueue(value);
            return pump();
          });
        }

        return pump();
      },
    });

    // Return the stream with proper headers
    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });

  } catch (error) {
    console.error('SSE Proxy Error:', error);
    
    // Return an error event
    const errorEvent = `data: ${JSON.stringify({
      type: 'error',
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    })}\n\n`;
    
    return new Response(errorEvent, {
      status: 500,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }
}
