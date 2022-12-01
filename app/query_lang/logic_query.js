/**
 * This file was generated from app\query_lang\logic_query.peg
 * See https://canopy.jcoglan.com/ for documentation
 */

(function () {
  'use strict';

  function TreeNode (text, offset, elements) {
    this.text = text;
    this.offset = offset;
    this.elements = elements;
  }

  TreeNode.prototype.forEach = function (block, context) {
    for (var el = this.elements, i = 0, n = el.length; i < n; i++) {
      block.call(context, el[i], i, el);
    }
  };

  if (typeof Symbol !== 'undefined' && Symbol.iterator) {
    TreeNode.prototype[Symbol.iterator] = function () {
      return this.elements[Symbol.iterator]();
    };
  }

  var TreeNode1 = function (text, offset, elements) {
    TreeNode.apply(this, arguments);
    this['id'] = elements[0];
  };
  inherit(TreeNode1, TreeNode);

  var TreeNode2 = function (text, offset, elements) {
    TreeNode.apply(this, arguments);
    this['BinOp'] = elements[1];
    this['id'] = elements[3];
  };
  inherit(TreeNode2, TreeNode);

  var TreeNode3 = function (text, offset, elements) {
    TreeNode.apply(this, arguments);
    this['ID'] = elements[1];
  };
  inherit(TreeNode3, TreeNode);

  var FAILURE = {};

  var Grammar = {
    _read_query () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._query = this._cache._query || {};
      var cached = this._cache._query[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var index1 = this._offset, elements0 = new Array(2);
      var address1 = FAILURE;
      address1 = this._read_id();
      if (address1 !== FAILURE) {
        elements0[0] = address1;
        var address2 = FAILURE;
        var index2 = this._offset, elements1 = [], address3 = null;
        while (true) {
          var index3 = this._offset, elements2 = new Array(4);
          var address4 = FAILURE;
          var index4 = this._offset, elements3 = [], address5 = null;
          while (true) {
            var chunk0 = null, max0 = this._offset + 1;
            if (max0 <= this._inputSize) {
              chunk0 = this._input.substring(this._offset, max0);
            }
            if (chunk0 === ' ') {
              address5 = new TreeNode(this._input.substring(this._offset, this._offset + 1), this._offset, []);
              this._offset = this._offset + 1;
            } else {
              address5 = FAILURE;
              if (this._offset > this._failure) {
                this._failure = this._offset;
                this._expected = [];
              }
              if (this._offset === this._failure) {
                this._expected.push(['LogicListQuery::query', '" "']);
              }
            }
            if (address5 !== FAILURE) {
              elements3.push(address5);
            } else {
              break;
            }
          }
          if (elements3.length >= 0) {
            address4 = new TreeNode(this._input.substring(index4, this._offset), index4, elements3);
            this._offset = this._offset;
          } else {
            address4 = FAILURE;
          }
          if (address4 !== FAILURE) {
            elements2[0] = address4;
            var address6 = FAILURE;
            address6 = this._read_BinOp();
            if (address6 !== FAILURE) {
              elements2[1] = address6;
              var address7 = FAILURE;
              var index5 = this._offset, elements4 = [], address8 = null;
              while (true) {
                var chunk1 = null, max1 = this._offset + 1;
                if (max1 <= this._inputSize) {
                  chunk1 = this._input.substring(this._offset, max1);
                }
                if (chunk1 === ' ') {
                  address8 = new TreeNode(this._input.substring(this._offset, this._offset + 1), this._offset, []);
                  this._offset = this._offset + 1;
                } else {
                  address8 = FAILURE;
                  if (this._offset > this._failure) {
                    this._failure = this._offset;
                    this._expected = [];
                  }
                  if (this._offset === this._failure) {
                    this._expected.push(['LogicListQuery::query', '" "']);
                  }
                }
                if (address8 !== FAILURE) {
                  elements4.push(address8);
                } else {
                  break;
                }
              }
              if (elements4.length >= 0) {
                address7 = new TreeNode(this._input.substring(index5, this._offset), index5, elements4);
                this._offset = this._offset;
              } else {
                address7 = FAILURE;
              }
              if (address7 !== FAILURE) {
                elements2[2] = address7;
                var address9 = FAILURE;
                address9 = this._read_id();
                if (address9 !== FAILURE) {
                  elements2[3] = address9;
                } else {
                  elements2 = null;
                  this._offset = index3;
                }
              } else {
                elements2 = null;
                this._offset = index3;
              }
            } else {
              elements2 = null;
              this._offset = index3;
            }
          } else {
            elements2 = null;
            this._offset = index3;
          }
          if (elements2 === null) {
            address3 = FAILURE;
          } else {
            address3 = new TreeNode2(this._input.substring(index3, this._offset), index3, elements2);
            this._offset = this._offset;
          }
          if (address3 !== FAILURE) {
            elements1.push(address3);
          } else {
            break;
          }
        }
        if (elements1.length >= 0) {
          address2 = new TreeNode(this._input.substring(index2, this._offset), index2, elements1);
          this._offset = this._offset;
        } else {
          address2 = FAILURE;
        }
        if (address2 !== FAILURE) {
          elements0[1] = address2;
        } else {
          elements0 = null;
          this._offset = index1;
        }
      } else {
        elements0 = null;
        this._offset = index1;
      }
      if (elements0 === null) {
        address0 = FAILURE;
      } else {
        address0 = new TreeNode1(this._input.substring(index1, this._offset), index1, elements0);
        this._offset = this._offset;
      }
      this._cache._query[index0] = [address0, this._offset];
      return address0;
    },

    _read_id () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._id = this._cache._id || {};
      var cached = this._cache._id[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var index1 = this._offset, elements0 = new Array(2);
      var address1 = FAILURE;
      var index2 = this._offset;
      address1 = this._read_NEG();
      if (address1 === FAILURE) {
        address1 = new TreeNode(this._input.substring(index2, index2), index2, []);
        this._offset = index2;
      }
      if (address1 !== FAILURE) {
        elements0[0] = address1;
        var address2 = FAILURE;
        address2 = this._read_ID();
        if (address2 !== FAILURE) {
          elements0[1] = address2;
        } else {
          elements0 = null;
          this._offset = index1;
        }
      } else {
        elements0 = null;
        this._offset = index1;
      }
      if (elements0 === null) {
        address0 = FAILURE;
      } else {
        address0 = new TreeNode3(this._input.substring(index1, this._offset), index1, elements0);
        this._offset = this._offset;
      }
      this._cache._id[index0] = [address0, this._offset];
      return address0;
    },

    _read_NEG () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._NEG = this._cache._NEG || {};
      var cached = this._cache._NEG[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var chunk0 = null, max0 = this._offset + 1;
      if (max0 <= this._inputSize) {
        chunk0 = this._input.substring(this._offset, max0);
      }
      if (chunk0 === '-') {
        address0 = new TreeNode(this._input.substring(this._offset, this._offset + 1), this._offset, []);
        this._offset = this._offset + 1;
      } else {
        address0 = FAILURE;
        if (this._offset > this._failure) {
          this._failure = this._offset;
          this._expected = [];
        }
        if (this._offset === this._failure) {
          this._expected.push(['LogicListQuery::NEG', '"-"']);
        }
      }
      this._cache._NEG[index0] = [address0, this._offset];
      return address0;
    },

    _read_BinOp () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._BinOp = this._cache._BinOp || {};
      var cached = this._cache._BinOp[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var index1 = this._offset;
      var chunk0 = null, max0 = this._offset + 1;
      if (max0 <= this._inputSize) {
        chunk0 = this._input.substring(this._offset, max0);
      }
      if (chunk0 === '|') {
        address0 = new TreeNode(this._input.substring(this._offset, this._offset + 1), this._offset, []);
        this._offset = this._offset + 1;
      } else {
        address0 = FAILURE;
        if (this._offset > this._failure) {
          this._failure = this._offset;
          this._expected = [];
        }
        if (this._offset === this._failure) {
          this._expected.push(['LogicListQuery::BinOp', '"|"']);
        }
      }
      if (address0 === FAILURE) {
        this._offset = index1;
        var chunk1 = null, max1 = this._offset + 1;
        if (max1 <= this._inputSize) {
          chunk1 = this._input.substring(this._offset, max1);
        }
        if (chunk1 === '&') {
          address0 = new TreeNode(this._input.substring(this._offset, this._offset + 1), this._offset, []);
          this._offset = this._offset + 1;
        } else {
          address0 = FAILURE;
          if (this._offset > this._failure) {
            this._failure = this._offset;
            this._expected = [];
          }
          if (this._offset === this._failure) {
            this._expected.push(['LogicListQuery::BinOp', '"&"']);
          }
        }
        if (address0 === FAILURE) {
          this._offset = index1;
        }
      }
      this._cache._BinOp[index0] = [address0, this._offset];
      return address0;
    },

    _read_ID () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._ID = this._cache._ID || {};
      var cached = this._cache._ID[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var index1 = this._offset;
      address0 = this._read_contemporary_meaning();
      if (address0 === FAILURE) {
        this._offset = index1;
        address0 = this._read_synt_function_of_anchor();
        if (address0 === FAILURE) {
          this._offset = index1;
        }
      }
      this._cache._ID[index0] = [address0, this._offset];
      return address0;
    },

    _read_contemporary_meaning () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._contemporary_meaning = this._cache._contemporary_meaning || {};
      var cached = this._cache._contemporary_meaning[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var index1 = this._offset;
      var chunk0 = null, max0 = this._offset + 14;
      if (max0 <= this._inputSize) {
        chunk0 = this._input.substring(this._offset, max0);
      }
      if (chunk0 !== null && chunk0.toLowerCase() === 'large quantity'.toLowerCase()) {
        address0 = new TreeNode(this._input.substring(this._offset, this._offset + 14), this._offset, []);
        this._offset = this._offset + 14;
      } else {
        address0 = FAILURE;
        if (this._offset > this._failure) {
          this._failure = this._offset;
          this._expected = [];
        }
        if (this._offset === this._failure) {
          this._expected.push(['LogicListQuery::contemporary_meaning', '`large quantity`']);
        }
      }
      if (address0 === FAILURE) {
        this._offset = index1;
        var chunk1 = null, max1 = this._offset + 19;
        if (max1 <= this._inputSize) {
          chunk1 = this._input.substring(this._offset, max1);
        }
        if (chunk1 !== null && chunk1.toLowerCase() === 'negative assessment'.toLowerCase()) {
          address0 = new TreeNode(this._input.substring(this._offset, this._offset + 19), this._offset, []);
          this._offset = this._offset + 19;
        } else {
          address0 = FAILURE;
          if (this._offset > this._failure) {
            this._failure = this._offset;
            this._expected = [];
          }
          if (this._offset === this._failure) {
            this._expected.push(['LogicListQuery::contemporary_meaning', '`negative assessment`']);
          }
        }
        if (address0 === FAILURE) {
          this._offset = index1;
          var chunk2 = null, max2 = this._offset + 7;
          if (max2 <= this._inputSize) {
            chunk2 = this._input.substring(this._offset, max2);
          }
          if (chunk2 !== null && chunk2.toLowerCase() === 'booster'.toLowerCase()) {
            address0 = new TreeNode(this._input.substring(this._offset, this._offset + 7), this._offset, []);
            this._offset = this._offset + 7;
          } else {
            address0 = FAILURE;
            if (this._offset > this._failure) {
              this._failure = this._offset;
              this._expected = [];
            }
            if (this._offset === this._failure) {
              this._expected.push(['LogicListQuery::contemporary_meaning', '`booster`']);
            }
          }
          if (address0 === FAILURE) {
            this._offset = index1;
          }
        }
      }
      this._cache._contemporary_meaning[index0] = [address0, this._offset];
      return address0;
    },

    _read_synt_function_of_anchor () {
      var address0 = FAILURE, index0 = this._offset;
      this._cache._synt_function_of_anchor = this._cache._synt_function_of_anchor || {};
      var cached = this._cache._synt_function_of_anchor[index0];
      if (cached) {
        this._offset = cached[1];
        return cached[0];
      }
      var index1 = this._offset;
      var chunk0 = null, max0 = this._offset + 8;
      if (max0 <= this._inputSize) {
        chunk0 = this._input.substring(this._offset, max0);
      }
      if (chunk0 !== null && chunk0.toLowerCase() === 'Argument'.toLowerCase()) {
        address0 = new TreeNode(this._input.substring(this._offset, this._offset + 8), this._offset, []);
        this._offset = this._offset + 8;
      } else {
        address0 = FAILURE;
        if (this._offset > this._failure) {
          this._failure = this._offset;
          this._expected = [];
        }
        if (this._offset === this._failure) {
          this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Argument`']);
        }
      }
      if (address0 === FAILURE) {
        this._offset = index1;
        var chunk1 = null, max1 = this._offset + 11;
        if (max1 <= this._inputSize) {
          chunk1 = this._input.substring(this._offset, max1);
        }
        if (chunk1 !== null && chunk1.toLowerCase() === 'Coordinator'.toLowerCase()) {
          address0 = new TreeNode(this._input.substring(this._offset, this._offset + 11), this._offset, []);
          this._offset = this._offset + 11;
        } else {
          address0 = FAILURE;
          if (this._offset > this._failure) {
            this._failure = this._offset;
            this._expected = [];
          }
          if (this._offset === this._failure) {
            this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Coordinator`']);
          }
        }
        if (address0 === FAILURE) {
          this._offset = index1;
          var chunk2 = null, max2 = this._offset + 18;
          if (max2 <= this._inputSize) {
            chunk2 = this._input.substring(this._offset, max2);
          }
          if (chunk2 !== null && chunk2.toLowerCase() === 'Discourse Particle'.toLowerCase()) {
            address0 = new TreeNode(this._input.substring(this._offset, this._offset + 18), this._offset, []);
            this._offset = this._offset + 18;
          } else {
            address0 = FAILURE;
            if (this._offset > this._failure) {
              this._failure = this._offset;
              this._expected = [];
            }
            if (this._offset === this._failure) {
              this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Discourse Particle`']);
            }
          }
          if (address0 === FAILURE) {
            this._offset = index1;
            var chunk3 = null, max3 = this._offset + 10;
            if (max3 <= this._inputSize) {
              chunk3 = this._input.substring(this._offset, max3);
            }
            if (chunk3 !== null && chunk3.toLowerCase() === 'Government'.toLowerCase()) {
              address0 = new TreeNode(this._input.substring(this._offset, this._offset + 10), this._offset, []);
              this._offset = this._offset + 10;
            } else {
              address0 = FAILURE;
              if (this._offset > this._failure) {
                this._failure = this._offset;
                this._expected = [];
              }
              if (this._offset === this._failure) {
                this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Government`']);
              }
            }
            if (address0 === FAILURE) {
              this._offset = index1;
              var chunk4 = null, max4 = this._offset + 16;
              if (max4 <= this._inputSize) {
                chunk4 = this._input.substring(this._offset, max4);
              }
              if (chunk4 !== null && chunk4.toLowerCase() === 'Matrix Predicate'.toLowerCase()) {
                address0 = new TreeNode(this._input.substring(this._offset, this._offset + 16), this._offset, []);
                this._offset = this._offset + 16;
              } else {
                address0 = FAILURE;
                if (this._offset > this._failure) {
                  this._failure = this._offset;
                  this._expected = [];
                }
                if (this._offset === this._failure) {
                  this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Matrix Predicate`']);
                }
              }
              if (address0 === FAILURE) {
                this._offset = index1;
                var chunk5 = null, max5 = this._offset + 8;
                if (max5 <= this._inputSize) {
                  chunk5 = this._input.substring(this._offset, max5);
                }
                if (chunk5 !== null && chunk5.toLowerCase() === 'Modifier'.toLowerCase()) {
                  address0 = new TreeNode(this._input.substring(this._offset, this._offset + 8), this._offset, []);
                  this._offset = this._offset + 8;
                } else {
                  address0 = FAILURE;
                  if (this._offset > this._failure) {
                    this._failure = this._offset;
                    this._expected = [];
                  }
                  if (this._offset === this._failure) {
                    this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Modifier`']);
                  }
                }
                if (address0 === FAILURE) {
                  this._offset = index1;
                  var chunk6 = null, max6 = this._offset + 18;
                  if (max6 <= this._inputSize) {
                    chunk6 = this._input.substring(this._offset, max6);
                  }
                  if (chunk6 !== null && chunk6.toLowerCase() === 'Nominal Quantifier'.toLowerCase()) {
                    address0 = new TreeNode(this._input.substring(this._offset, this._offset + 18), this._offset, []);
                    this._offset = this._offset + 18;
                  } else {
                    address0 = FAILURE;
                    if (this._offset > this._failure) {
                      this._failure = this._offset;
                      this._expected = [];
                    }
                    if (this._offset === this._failure) {
                      this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Nominal Quantifier`']);
                    }
                  }
                  if (address0 === FAILURE) {
                    this._offset = index1;
                    var chunk7 = null, max7 = this._offset + 6;
                    if (max7 <= this._inputSize) {
                      chunk7 = this._input.substring(this._offset, max7);
                    }
                    if (chunk7 !== null && chunk7.toLowerCase() === 'Object'.toLowerCase()) {
                      address0 = new TreeNode(this._input.substring(this._offset, this._offset + 6), this._offset, []);
                      this._offset = this._offset + 6;
                    } else {
                      address0 = FAILURE;
                      if (this._offset > this._failure) {
                        this._failure = this._offset;
                        this._expected = [];
                      }
                      if (this._offset === this._failure) {
                        this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Object`']);
                      }
                    }
                    if (address0 === FAILURE) {
                      this._offset = index1;
                      var chunk8 = null, max8 = this._offset + 13;
                      if (max8 <= this._inputSize) {
                        chunk8 = this._input.substring(this._offset, max8);
                      }
                      if (chunk8 !== null && chunk8.toLowerCase() === 'Parenthetical'.toLowerCase()) {
                        address0 = new TreeNode(this._input.substring(this._offset, this._offset + 13), this._offset, []);
                        this._offset = this._offset + 13;
                      } else {
                        address0 = FAILURE;
                        if (this._offset > this._failure) {
                          this._failure = this._offset;
                          this._expected = [];
                        }
                        if (this._offset === this._failure) {
                          this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Parenthetical`']);
                        }
                      }
                      if (address0 === FAILURE) {
                        this._offset = index1;
                        var chunk9 = null, max9 = this._offset + 23;
                        if (max9 <= this._inputSize) {
                          chunk9 = this._input.substring(this._offset, max9);
                        }
                        if (chunk9 !== null && chunk9.toLowerCase() === 'Praedicative Expression'.toLowerCase()) {
                          address0 = new TreeNode(this._input.substring(this._offset, this._offset + 23), this._offset, []);
                          this._offset = this._offset + 23;
                        } else {
                          address0 = FAILURE;
                          if (this._offset > this._failure) {
                            this._failure = this._offset;
                            this._expected = [];
                          }
                          if (this._offset === this._failure) {
                            this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Praedicative Expression`']);
                          }
                        }
                        if (address0 === FAILURE) {
                          this._offset = index1;
                          var chunk10 = null, max10 = this._offset + 7;
                          if (max10 <= this._inputSize) {
                            chunk10 = this._input.substring(this._offset, max10);
                          }
                          if (chunk10 !== null && chunk10.toLowerCase() === 'Subject'.toLowerCase()) {
                            address0 = new TreeNode(this._input.substring(this._offset, this._offset + 7), this._offset, []);
                            this._offset = this._offset + 7;
                          } else {
                            address0 = FAILURE;
                            if (this._offset > this._failure) {
                              this._failure = this._offset;
                              this._expected = [];
                            }
                            if (this._offset === this._failure) {
                              this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Subject`']);
                            }
                          }
                          if (address0 === FAILURE) {
                            this._offset = index1;
                            var chunk11 = null, max11 = this._offset + 12;
                            if (max11 <= this._inputSize) {
                              chunk11 = this._input.substring(this._offset, max11);
                            }
                            if (chunk11 !== null && chunk11.toLowerCase() === 'Subordinator'.toLowerCase()) {
                              address0 = new TreeNode(this._input.substring(this._offset, this._offset + 12), this._offset, []);
                              this._offset = this._offset + 12;
                            } else {
                              address0 = FAILURE;
                              if (this._offset > this._failure) {
                                this._failure = this._offset;
                                this._expected = [];
                              }
                              if (this._offset === this._failure) {
                                this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Subordinator`']);
                              }
                            }
                            if (address0 === FAILURE) {
                              this._offset = index1;
                              var chunk12 = null, max12 = this._offset + 14;
                              if (max12 <= this._inputSize) {
                                chunk12 = this._input.substring(this._offset, max12);
                              }
                              if (chunk12 !== null && chunk12.toLowerCase() === 'Verb Predicate'.toLowerCase()) {
                                address0 = new TreeNode(this._input.substring(this._offset, this._offset + 14), this._offset, []);
                                this._offset = this._offset + 14;
                              } else {
                                address0 = FAILURE;
                                if (this._offset > this._failure) {
                                  this._failure = this._offset;
                                  this._expected = [];
                                }
                                if (this._offset === this._failure) {
                                  this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Verb Predicate`']);
                                }
                              }
                              if (address0 === FAILURE) {
                                this._offset = index1;
                                var chunk13 = null, max13 = this._offset + 14;
                                if (max13 <= this._inputSize) {
                                  chunk13 = this._input.substring(this._offset, max13);
                                }
                                if (chunk13 !== null && chunk13.toLowerCase() === 'Word-Formation'.toLowerCase()) {
                                  address0 = new TreeNode(this._input.substring(this._offset, this._offset + 14), this._offset, []);
                                  this._offset = this._offset + 14;
                                } else {
                                  address0 = FAILURE;
                                  if (this._offset > this._failure) {
                                    this._failure = this._offset;
                                    this._expected = [];
                                  }
                                  if (this._offset === this._failure) {
                                    this._expected.push(['LogicListQuery::synt_function_of_anchor', '`Word-Formation`']);
                                  }
                                }
                                if (address0 === FAILURE) {
                                  this._offset = index1;
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      this._cache._synt_function_of_anchor[index0] = [address0, this._offset];
      return address0;
    }
  };

  var Parser = function(input, actions, types) {
    this._input = input;
    this._inputSize = input.length;
    this._actions = actions;
    this._types = types;
    this._offset = 0;
    this._cache = {};
    this._failure = 0;
    this._expected = [];
  };

  Parser.prototype.parse = function() {
    var tree = this._read_query();
    if (tree !== FAILURE && this._offset === this._inputSize) {
      return tree;
    }
    if (this._expected.length === 0) {
      this._failure = this._offset;
      this._expected.push(['LogicListQuery', '<EOF>']);
    }
    this.constructor.lastError = { offset: this._offset, expected: this._expected };
    throw new SyntaxError(formatError(this._input, this._failure, this._expected));
  };

  Object.assign(Parser.prototype, Grammar);


  function parse(input, options) {
    options = options || {};
    var parser = new Parser(input, options.actions, options.types);
    return parser.parse();
  }

  function formatError(input, offset, expected) {
    var lines = input.split(/\n/g),
        lineNo = 0,
        position = 0;

    while (position <= offset) {
      position += lines[lineNo].length + 1;
      lineNo += 1;
    }

    var line = lines[lineNo - 1],
        message = 'Line ' + lineNo + ': expected one of:\n\n';

    for (var i = 0; i < expected.length; i++) {
      message += '    - ' + expected[i][1] + ' from ' + expected[i][0] + '\n';
    }
    var number = lineNo.toString();
    while (number.length < 6) number = ' ' + number;
    message += '\n' + number + ' | ' + line + '\n';

    position -= line.length + 10;

    while (position < offset) {
      message += ' ';
      position += 1;
    }
    return message + '^';
  }

  function inherit(subclass, parent) {
    function chain () {};
    chain.prototype = parent.prototype;
    subclass.prototype = new chain();
    subclass.prototype.constructor = subclass;
  }


  var exported = { Grammar: Grammar, Parser: Parser, parse: parse };

  if (typeof require === 'function' && typeof exports === 'object') {
    Object.assign(exports, exported);
  } else {
    var ns = (typeof this === 'undefined') ? window : this;
    ns.LogicListQuery = exported;
  }
})();
