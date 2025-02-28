################################################################################
#                                                                              
#  "I understand there's a guy inside me who wants to lay in bed,              
#   smoke weed 🍃 all day, and watch cartoons and old movies.                     
#   My whole life is a series of stratagems to avoid, and outwit, that guy."  
#                                                                              
#   - Anthony Bourdain                                                                                                                         
#                                                                              
################################################################################
#
#
#
"""
main.py

Root-level entry point for local development:
   $ python main.py
"""

import uvicorn
from app.api.main import app

if __name__ == "__main__":
    # Start the FastAPI application on port 8000 with auto-reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
