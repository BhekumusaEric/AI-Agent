/**
 * AI Agent Interface JavaScript
 */

$(document).ready(function() {
    // MIU System - Get Next States
    $('#miu-next-states-btn').click(function() {
        const state = $('#miu-state').val();
        
        if (!state) {
            alert('Please enter a state');
            return;
        }
        
        $.ajax({
            url: '/api/miu/next_states',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ state: state }),
            success: function(response) {
                if (response.error) {
                    $('#miu-next-states-result').html(`<div class="alert alert-danger">${response.error}</div>`);
                    return;
                }
                
                const nextStates = response.next_states;
                let html = '<h4>Next States:</h4>';
                
                if (nextStates.length === 0) {
                    html += '<p>No next states available.</p>';
                } else {
                    html += '<ul>';
                    nextStates.forEach(function(nextState) {
                        html += `<li>${nextState}</li>`;
                    });
                    html += '</ul>';
                }
                
                $('#miu-next-states-result').html(html);
            },
            error: function() {
                $('#miu-next-states-result').html('<div class="alert alert-danger">Error fetching next states</div>');
            }
        });
    });
    
    // MIU System - Search
    $('#miu-form').submit(function(e) {
        e.preventDefault();
        
        const initialState = $('#miu-initial-state').val();
        const goalState = $('#miu-goal-state').val();
        const algorithm = $('#miu-algorithm').val();
        const maxIterations = $('#miu-max-iterations').val();
        
        if (!initialState || !goalState) {
            alert('Please enter initial and goal states');
            return;
        }
        
        // Show loading indicator
        $('#miu-loading').show();
        $('#miu-search-result').hide();
        
        $.ajax({
            url: '/api/miu/search',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                initial_state: initialState,
                goal_state: goalState,
                algorithm: algorithm,
                max_iterations: maxIterations
            }),
            success: function(response) {
                // Hide loading indicator
                $('#miu-loading').hide();
                
                if (response.error) {
                    alert(response.error);
                    return;
                }
                
                // Display results
                let resultInfo = `<p><strong>Iterations:</strong> ${response.iterations}</p>`;
                resultInfo += `<p><strong>Visited Nodes:</strong> ${response.visited_nodes_count}</p>`;
                
                if (response.solution_found) {
                    resultInfo += `<p><strong>Solution Found:</strong> Yes</p>`;
                    resultInfo += `<p><strong>Path Length:</strong> ${response.path_length} steps</p>`;
                    
                    let pathHtml = '';
                    response.path.forEach(function(step) {
                        pathHtml += `<div class="path-step">`;
                        pathHtml += `<strong>${step.step}.</strong> `;
                        pathHtml += `${step.action} → ${step.state}`;
                        pathHtml += `</div>`;
                    });
                    
                    $('#miu-path').html(pathHtml);
                    $('#miu-path-container').show();
                } else {
                    resultInfo += `<p><strong>Solution Found:</strong> No</p>`;
                    $('#miu-path-container').hide();
                }
                
                $('#miu-result-info').html(resultInfo);
                
                // Display graph
                if (response.graph_image) {
                    $('#miu-graph').attr('src', `data:image/png;base64,${response.graph_image}`);
                    $('#miu-graph-container').show();
                } else {
                    $('#miu-graph-container').hide();
                }
                
                $('#miu-search-result').show();
            },
            error: function() {
                $('#miu-loading').hide();
                alert('Error running search');
            }
        });
    });
    
    // Maze Environment - Generate Maze
    $('#maze-form').submit(function(e) {
        e.preventDefault();
        
        const width = $('#maze-width').val();
        const height = $('#maze-height').val();
        const wallProb = $('#maze-wall-prob').val();
        const seed = $('#maze-seed').val();
        
        // Show loading indicator
        $('#maze-loading').show();
        $('#maze-result').hide();
        $('#maze-search-result').hide();
        
        $.ajax({
            url: '/api/maze/generate',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                width: width,
                height: height,
                wall_prob: wallProb,
                seed: seed
            }),
            success: function(response) {
                // Hide loading indicator
                $('#maze-loading').hide();
                
                if (response.error) {
                    alert(response.error);
                    return;
                }
                
                // Store maze data for search
                window.mazeData = response;
                
                // Display maze
                if (response.maze_image) {
                    $('#maze-image').attr('src', `data:image/png;base64,${response.maze_image}`);
                    $('#maze-result').show();
                }
                
                // Enable search button
                $('#maze-search-form button').prop('disabled', false);
            },
            error: function() {
                $('#maze-loading').hide();
                alert('Error generating maze');
            }
        });
    });
    
    // Maze Environment - Search
    $('#maze-search-form').submit(function(e) {
        e.preventDefault();
        
        if (!window.mazeData) {
            alert('Please generate a maze first');
            return;
        }
        
        const algorithm = $('#maze-algorithm').val();
        
        // Show loading indicator
        $('#maze-search-loading').show();
        $('#maze-search-result').hide();
        
        $.ajax({
            url: '/api/maze/search',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                grid: window.mazeData.grid,
                start: window.mazeData.start,
                goal: window.mazeData.goal,
                algorithm: algorithm
            }),
            success: function(response) {
                // Hide loading indicator
                $('#maze-search-loading').hide();
                
                if (response.error) {
                    alert(response.error);
                    return;
                }
                
                // Display results
                let resultInfo = `<p><strong>Iterations:</strong> ${response.iterations}</p>`;
                resultInfo += `<p><strong>Visited Nodes:</strong> ${response.visited_nodes_count}</p>`;
                
                if (response.solution_found) {
                    resultInfo += `<p><strong>Solution Found:</strong> Yes</p>`;
                    resultInfo += `<p><strong>Path Length:</strong> ${response.path_length} steps</p>`;
                    
                    // Display first few steps of the path
                    let pathHtml = '';
                    const maxStepsToShow = 5;
                    const stepsToShow = Math.min(maxStepsToShow, response.path.length);
                    
                    for (let i = 0; i < stepsToShow; i++) {
                        const step = response.path[i];
                        pathHtml += `<div class="path-step">`;
                        pathHtml += `<strong>${step.step}.</strong> `;
                        pathHtml += `${step.action} → (${step.state[0]}, ${step.state[1]})`;
                        pathHtml += `</div>`;
                    }
                    
                    if (response.path.length > maxStepsToShow) {
                        pathHtml += `<div class="path-step">... (${response.path.length - maxStepsToShow} more steps)</div>`;
                    }
                    
                    $('#maze-path').html(pathHtml);
                } else {
                    resultInfo += `<p><strong>Solution Found:</strong> No</p>`;
                    $('#maze-path').html('<p>No solution found.</p>');
                }
                
                $('#maze-result-info').html(resultInfo);
                
                // Display solution image
                if (response.maze_solution_image) {
                    $('#maze-solution-image').attr('src', `data:image/png;base64,${response.maze_solution_image}`);
                }
                
                $('#maze-search-result').show();
            },
            error: function() {
                $('#maze-search-loading').hide();
                alert('Error running search');
            }
        });
    });
});
