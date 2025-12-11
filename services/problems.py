"""
Problem database for coding challenges.

This module contains coding problems similar to LeetCode challenges
with test cases and starter code for multiple languages.
"""

PROBLEMS = {
    1: {
        "id": 1,
        "title": "Two Sum",
        "difficulty": "Easy",
        "category": "Arrays",
        "description": """
            <p>Given an array of integers <code>nums</code> and an integer <code>target</code>, 
            return indices of the two numbers such that they add up to <code>target</code>.</p>
            
            <p>You may assume that each input would have <strong>exactly one solution</strong>, 
            and you may not use the same element twice.</p>
            
            <p>You can return the answer in any order.</p>
        """,
        "examples": [
            {
                "input": "nums = [2,7,11,15], target = 9",
                "output": "[0,1]",
                "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
            },
            {
                "input": "nums = [3,2,4], target = 6",
                "output": "[1,2]",
                "explanation": "Because nums[1] + nums[2] == 6, we return [1, 2]."
            }
        ],
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists."
        ],
        "hints": [
            "Try using a hash map to store numbers you've seen and their indices.",
            "For each number, check if target - number exists in your hash map."
        ],
        "starter_code": {
            "python": """def twoSum(nums, target):
    # Write your code here
    pass

# Test your function
if __name__ == "__main__":
    import json
    nums = json.loads(input())
    target = int(input())
    result = twoSum(nums, target)
    print(json.dumps(result))""",
            "cpp": """#include <iostream>
#include <vector>
#include <json/json.h>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your code here
    return {};
}

int main() {
    // Input handling
    string line;
    getline(cin, line);
    // Parse JSON input
    Json::Value root;
    Json::Reader reader;
    reader.parse(line, root);
    
    vector<int> nums;
    for (const auto& val : root) {
        nums.push_back(val.asInt());
    }
    
    int target;
    cin >> target;
    
    vector<int> result = twoSum(nums, target);
    
    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        cout << result[i];
        if (i < result.size() - 1) cout << ",";
    }
    cout << "]" << endl;
    
    return 0;
}""",
            "java": """import java.util.*;
import com.google.gson.*;

public class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Write your code here
        return new int[]{};
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Gson gson = new Gson();
        
        String numsJson = scanner.nextLine();
        int[] nums = gson.fromJson(numsJson, int[].class);
        
        int target = scanner.nextInt();
        
        Solution solution = new Solution();
        int[] result = solution.twoSum(nums, target);
        
        System.out.println(Arrays.toString(result));
    }
}"""
        },
        "test_cases": [
            {
                "input": ["[2,7,11,15]", "9"],
                "expected_output": "[0,1]"
            },
            {
                "input": ["[3,2,4]", "6"],
                "expected_output": "[1,2]"
            },
            {
                "input": ["[3,3]", "6"],
                "expected_output": "[0,1]"
            }
        ]
    },
    2: {
        "id": 2,
        "title": "Reverse String",
        "difficulty": "Easy",
        "category": "Strings",
        "description": """
            <p>Write a function that reverses a string. The input string is given as an array of characters <code>s</code>.</p>
            
            <p>You must do this by modifying the input array in-place with O(1) extra memory.</p>
        """,
        "examples": [
            {
                "input": 's = ["h","e","l","l","o"]',
                "output": '["o","l","l","e","h"]',
                "explanation": ""
            },
            {
                "input": 's = ["H","a","n","n","a","h"]',
                "output": '["h","a","n","n","a","H"]',
                "explanation": ""
            }
        ],
        "constraints": [
            "1 <= s.length <= 10^5",
            "s[i] is a printable ascii character."
        ],
        "hints": [
            "Use two pointers approach, one from start and one from end.",
            "Swap characters at both pointers and move them towards center."
        ],
        "starter_code": {
            "python": """def reverseString(s):
    # Write your code here
    # Modify s in-place
    pass

# Test your function
if __name__ == "__main__":
    import json
    s = json.loads(input())
    reverseString(s)
    print(json.dumps(s))""",
            "cpp": """#include <iostream>
#include <vector>
#include <string>
using namespace std;

void reverseString(vector<char>& s) {
    // Write your code here
}

int main() {
    string line;
    getline(cin, line);
    
    vector<char> s;
    for (char c : line) {
        if (c != '[' && c != ']' && c != '"' && c != ',' && c != ' ') {
            s.push_back(c);
        }
    }
    
    reverseString(s);
    
    cout << "[";
    for (size_t i = 0; i < s.size(); i++) {
        cout << "\\"" << s[i] << "\\"";
        if (i < s.size() - 1) cout << ",";
    }
    cout << "]" << endl;
    
    return 0;
}""",
            "java": """import java.util.*;

public class Solution {
    public void reverseString(char[] s) {
        // Write your code here
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        
        // Parse input
        String[] parts = input.replace("[", "").replace("]", "")
                             .replace("\\"", "").split(",");
        char[] s = new char[parts.length];
        for (int i = 0; i < parts.length; i++) {
            s[i] = parts[i].trim().charAt(0);
        }
        
        Solution solution = new Solution();
        solution.reverseString(s);
        
        System.out.print("[");
        for (int i = 0; i < s.length; i++) {
            System.out.print("\\"" + s[i] + "\\"");
            if (i < s.length - 1) System.out.print(",");
        }
        System.out.println("]");
    }
}"""
        },
        "test_cases": [
            {
                "input": ['["h","e","l","l","o"]'],
                "expected_output": '["o","l","l","e","h"]'
            },
            {
                "input": ['["H","a","n","n","a","h"]'],
                "expected_output": '["h","a","n","n","a","H"]'
            }
        ]
    },
    3: {
        "id": 3,
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "category": "Stack",
        "description": """
            <p>Given a string <code>s</code> containing just the characters <code>'('</code>, <code>')'</code>, 
            <code>'{'</code>, <code>'}'</code>, <code>'['</code> and <code>']'</code>, 
            determine if the input string is valid.</p>
            
            <p>An input string is valid if:</p>
            <ol>
                <li>Open brackets must be closed by the same type of brackets.</li>
                <li>Open brackets must be closed in the correct order.</li>
                <li>Every close bracket has a corresponding open bracket of the same type.</li>
            </ol>
        """,
        "examples": [
            {
                "input": 's = "()"',
                "output": "true",
                "explanation": ""
            },
            {
                "input": 's = "()[]{}"',
                "output": "true",
                "explanation": ""
            },
            {
                "input": 's = "(]"',
                "output": "false",
                "explanation": ""
            }
        ],
        "constraints": [
            "1 <= s.length <= 10^4",
            "s consists of parentheses only '()[]{}'."
        ],
        "hints": [
            "Use a stack data structure.",
            "Push opening brackets onto the stack.",
            "When you encounter a closing bracket, check if it matches the top of the stack."
        ],
        "starter_code": {
            "python": """def isValid(s):
    # Write your code here
    pass

# Test your function
if __name__ == "__main__":
    s = input().strip()
    result = isValid(s)
    print(str(result).lower())""",
            "cpp": """#include <iostream>
#include <string>
using namespace std;

bool isValid(string s) {
    // Write your code here
    return false;
}

int main() {
    string s;
    cin >> s;
    
    bool result = isValid(s);
    cout << (result ? "true" : "false") << endl;
    
    return 0;
}""",
            "java": """import java.util.*;

public class Solution {
    public boolean isValid(String s) {
        // Write your code here
        return false;
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String s = scanner.next();
        
        Solution solution = new Solution();
        boolean result = solution.isValid(s);
        
        System.out.println(result);
    }
}"""
        },
        "test_cases": [
            {
                "input": ["()"],
                "expected_output": "true"
            },
            {
                "input": ["()[]{}"],
                "expected_output": "true"
            },
            {
                "input": ["(]"],
                "expected_output": "false"
            },
            {
                "input": ["([)]"],
                "expected_output": "false"
            },
            {
                "input": ["{[]}"],
                "expected_output": "true"
            }
        ]
    }
}


def get_problem(problem_id):
    """Get a problem by ID"""
    return PROBLEMS.get(problem_id)


def get_all_problems():
    """Get all problems"""
    return list(PROBLEMS.values())


def get_random_problem():
    """Get a random problem"""
    import random
    return random.choice(list(PROBLEMS.values()))


